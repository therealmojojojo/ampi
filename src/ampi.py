from xmlrpc.client import boolean
from components import music_box
from components.hardware.buttons import ButtonsController
from components.database import database
from components.hardware.nfc_cmd import NFCReader
from components.hardware.screen import EpdDisplay
from components.hardware.volume import VolumeControl
from components.model.musicbox import MusicBox, TrackMetadata
from components.model.event import AmpiEvent
from utils.logger import LogFormatter
import utils.configuration
import utils.logger
import argparse
import os
import logging
import threading
import time

logger = None

temp_files_folder = utils.configuration.get_property(
    utils.configuration.CONFIG_TEMP_FILES_FOLDER)
currently_playing_file = temp_files_folder + "/" + "currentlyplaying.txt"

monitor_frequency = int(utils.configuration.get_property(
    utils.configuration.CONFIG_MONITOR_FREQUENCY, 2))

use_screen = boolean(utils.configuration.get_property(
    utils.configuration.CONFIG_USE_SCREEN, False))
use_buttons = boolean(utils.configuration.get_property(
    utils.configuration.CONFIG_USE_SCREEN, False))
use_nfc = boolean(utils.configuration.get_property(
    utils.configuration.CONFIG_USE_NFC, False))


class StatusMonitor(threading.Thread):
    def __init__(self, controller, event_handler):
        threading.Thread.__init__(self)
        self.controller = controller
        self.running = True
        self.event_handler = event_handler

    def exit_gracefully(self):
        self.running = False

    def run(self):
        logger.debug("Status monitor started. Frequency = %d",
                     monitor_frequency)
        while self.running:
            try:
                if not self.running:
                    break
                logger.debug("Checking changes")
                track, state = self.controller.info()
                if track.track_name != self.controller.current_track.track_name:
                    logger.debug("Track changed")
                    self.controller.current_track = track
                    self.event_handler(AmpiEvent.TRACK_CHANGED, track)

                if state != self.controller.current_status:
                    logger.debug("Status changed")
                    self.controller.current_status = state
                    self.event_handler(AmpiEvent.PLAYING_STATUS_CHANGED, state)
            except:
                logger.warning("Exception getting current track")
            time.sleep(monitor_frequency)
        logger.info("Status monitor shut down!")


class AmpiController:
    # states
    NON_INITIALIZED = 0
    READY = 1  # not doing nothing, waiting for input
    PLAYING = 2  # playing a playlist
    PAUSED = 3  # was playing, now paused, waiting for interraction
    RESTARTED = 4

    component_registry = []
    turn_on_off_state = 0
    playlist = None
    current_track = TrackMetadata()
    current_status = "Stopped"

    def __init__(self):
        self.player = None
        self.nfc_reader = None
        self.screen = None
        self.nfc_reader = None
        self.volume_control = None
        self.status_monitor = None
        self.buttons_controller = None
        self.running = True
        if use_screen:
            self.screen = EpdDisplay()
            self.screen.splash()
        else:
            logger.warning("Screen disabled by configuration")
        self.load_old_state()
        # init screen

    # saves pid & playslist on disk

    def save_state(self, playlist):
        with open(currently_playing_file, 'w', encoding='utf-8') as f:
            f.write(str(os.getpid())+"," + playlist)

    def load_old_state(self):
        line = None
        try:
            with open(currently_playing_file, 'r', encoding='utf-8') as f:
                line = f.readline()
        except FileNotFoundError:
            logger.warning(currently_playing_file + " file not found")
        if line is None:
            return None
        pid, playlist = line.split(",")
        if pid == str(os.getpid()):
            logger.debug("same pid")
        else:
            logger.debug("old pid:" + str(os.getpid()))

        self.playlist = playlist
        if self.playlist is not None:
            logger.info("Restarted. Previous Playlist: " + self.playlist)
            self.player = music_box.get_client(self.playlist)
            self.player.load_playlist(self.playlist)

    def refresh_screen(self):
        track = self.player.get_current_track()
        if track is not None:
            self.screen.refresh(track)

    def turn_on_off(self):
        if(self.turn_on_off_state):
            self.turn_on_off_state = 0
            logger.debug("Turning off...")
        else:
            self.turn_on_off_state = 1
            logger.debug("Turning on...")

    def play(self, nfc_string: str):
        logger.debug(nfc_string)
        if self.player is not None:
            if self.player.current_playlist == nfc_string:
                logger.debug("The playlist is already loaded")
                self.player.play()
                return
            # a playlist was played before
            else:
                self.player.close()
        logger.debug("New playlist received")

        self.player = music_box.get_client(nfc_string)
        if self.player is None:
            logger.debug("Invalid/Not supported playlist")
            return
        # if self.current_state == AmpiController.RESTARTED:
        self.player.play()
        logger.debug("Start playing " + nfc_string)
        self.save_state(nfc_string)

    def play_current(self):
        if self.player is not None:
            state = self.player.get_current_state()
            logger.debug("current state: %s", state)
            if state == MusicBox.PLAYING:
                logger.debug("Pausing")
                self.player.pause()
            else:
                logger.debug("Start playing")
                self.player.play()

    def volume_change(self, payload):
        if payload is not None:
            logger.debug("Volume changing request to %d", payload)
            if payload < 0 or payload > 100:
                payload = 30
            elif payload > 70:
                # limit volume to 70
                payload = 70
        else:
            logger.warning("Invalid volume value received")
        logger.debug("Changing volume to %d", payload)
        self.player.volume_change(payload)

    def next(self):
        if self.player is not None:
            self.player.next()
        logger.debug("Next")

        self.info()

    def back(self):
        if self.player is not None:
            self.player.back()
        self.info()
        logger.debug("Back")

    def fast_forward(self):
        logger.debug("Fast Forward 10 sec")

    def rewind(self):
        logger.debug("Rewind 10 sec")

    def pause(self):
        if self.player is not None:
            self.player.pause()
        self.info()
        logger.debug("Pause")

    def resume(self):
        if self.player is not None:
            self.player.resume()
        self.info()
        logger.debug("resume")

    def stop(self):
        if self.player is not None:
            self.player.stop()
        self.info()
        logger.debug("Stop")

    def mute(self):
        if self.player is not None:
            self.player.mute()
        logger.debug("Mute")

    def info(self):
        logger.debug("info")
        if self.player is not None:
            track = self.player.get_current_track()
            state = self.player.get_current_state()
        logger.debug("Status: %s Track: %s", state, track)
        return track, state

    def trigger_event(self, event: AmpiEvent, payload=None):
        if event is None:
            logger.debug("No event received. Ignore...")
            return
        if event == AmpiEvent.CARD_READ:
            logger.info("Card Read event received, UID=%s", payload)
            playlist = database.get_playlist(payload)
            logger.info("Playlist %s found for UID=%s", playlist, payload)
            if playlist is None:
                logger.debug("No playlist found for UID: %s", payload)
            self.play(playlist)
        elif event == AmpiEvent.VOLUME_CHANGE:
            self.volume_change(payload)
        elif event == AmpiEvent.NEXT_PRESSED:
            logger.debug("Next button pressed")
            self.next()
        elif event == AmpiEvent.PLAY_PRESSED:
            self.play_current()
        elif event == AmpiEvent.FFWD_PRESSED:
            pass
        elif event == AmpiEvent.BACK_PRESSED:
            self.back()
        elif event == AmpiEvent.RESET_PRESSED:
            self.turn_on_off()
        elif event == AmpiEvent.STOP_PRESSED:
            self.stop()
        elif event == AmpiEvent.MUTE_PRESSED:
            self.mute()
        elif event == AmpiEvent.TRACK_CHANGED:
            self.refresh_screen()
        elif event == AmpiEvent.PLAYING_STATUS_CHANGED:
            pass
        else:
            logger.debug("Ampi Controller has received an unsuported event")

    def exit_gracefully(self, *args):
        self.running = False

    def shutdown_ampi(self):
        logger.info("Shutting down")
        if self.player != None:
            self.player.close()
        if self.screen != None:
            self.screen.sleep()
        if self.volume_control != None:
            self.volume_control.exit_gracefully()
            self.volume_control.join()
        if self.buttons_controller != None:
            self.buttons_controller.exit_gracefully()
            self.buttons_controller.join()
        if self.nfc_reader != None:
            self.nfc_reader.exit_gracefully()
            self.nfc_reader.join()
        if self.status_monitor != None:
            self.status_monitor.exit_gracefully()
            self.status_monitor.join()
        logger.info("Ampi shutdown finished")

    def start_daemon(self):
        logger.info("Running ampi startup")
        if use_nfc:
            logger.warning("Init NFC")
            # init nfc reader
            self.nfc_reader = NFCReader(self.trigger_event)
            self.nfc_reader.start()
        else:
            logger.warning("NFC disabled by configuration")
        logger.warning("Init buttons")
        if use_buttons:
            # init buttons
            self.buttons_controller = ButtonsController(self.trigger_event)
            self.buttons_controller.start()
            # init volume knob
            self.volume_control = VolumeControl(self.trigger_event)
            self.volume_control.start()
        else:
            logger.warning("Buttons disabled by configuration")

        # init status monitor - needed because there are no track change events from the clients...
        self.status_monitor = StatusMonitor(self, self.trigger_event)
        self.status_monitor.start()
        logger.info("Ampi startup ended")
        while self.running:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                self.shutdown_ampi()
                break


if __name__ == '__main__':
    # init logging
    if (not utils.logger.setup_logging(console_log_output="stdout", console_log_level="debug", console_log_color=True,
        logfile_file="ampi.log", logfile_log_level="debug", logfile_log_color=False, logfile_log_datefmt='%Y/%m/%d %I:%M:%S %p',
                                       log_line_template="%(color_on)s[%(asctime)s ] [%(threadName)s] [%(levelname)-8s] [%(filename)s] [%(funcName)s] [%(lineno)d] %(message)s%(color_off)s")):
        logger.debug("Failed to setup logging.")
        exit(1)
    logger = logging.getLogger(__name__)
    log_level = utils.configuration.get_property(
        utils.configuration.CONFIG_LOG_LEVEL)
    if log_level is not None:
        logger.setLevel(log_level)
    ampi = AmpiController()
    parser = argparse.ArgumentParser(prog="ampi")
    parser.add_argument(
        "-d", "--daemon", help="start as daemon", action='store_true')
    parser.add_argument(
        "-p", "--play", help="start a playlist", nargs="*", required=False)
    parser.add_argument(
        "-a", "--action", choices=["stop", "next", "info", "pause", "resume"], nargs="*", required=False)
    parser.add_argument("-v", "--volume", nargs="*", required=False)
    args = parser.parse_args()
    config = vars(args)
    logger.debug(config)
    if config["play"] is not None:
        ampi.play(str(config["play"][0]))
    if config["volume"] is not None:
        ampi.volume_change(int(config["volume"][0]))
    if config["action"] == "stop":
        ampi.pause()
    elif config["action"] == "next":
        ampi.next()
    elif config["action"] == "info":
        logger.debug(ampi.info())
    elif config["action"] == "pause":
        ampi.pause()
    elif config["action"] == "resume":
        ampi.resume()
    elif config["daemon"]:
        ampi.start_daemon()
    else:
        pass
