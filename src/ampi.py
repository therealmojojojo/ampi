from components import music_box, database
from components.buttons import ButtonsController
from components.nfc_cmd import NFCReader
from components.volume import VolumeControl
from utils.event import AmpiEvent
from utils.logger import LogFormatter
import utils.configuration
import utils.logger
import argparse
import os
import logging

logger = None


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

    def __init__(self):
        self.player = None
        self.load_old_state()

    def start_deamon(self):
        logger.warning("Running ampi startup")
        logger.warning("Init NFC")
        # init nfc reader
        nfc_reader = NFCReader(self.trigger_event)
        nfc_reader.start()

        logger.warning("Init buttons")
        # init buttons
        buttons_controller = ButtonsController(self.trigger_event)
        buttons_controller.start()

        # init volume knob
        volume_control = VolumeControl(self.trigger_event)
        volume_control.start()

        # init screen
        logger.warning("Ampi startup ended")

    # saves pid & playslist on disk
    def save_state(self, playlist):
        with open('currentlyplaying.txt', 'w', encoding='utf-8') as f:
            f.write(str(os.getpid())+"," + playlist)

    def load_old_state(self):
        line = None
        try:
            with open('currentlyplaying.txt', 'r', encoding='utf-8') as f:
                line = f.readline()
        except FileNotFoundError:
            logger.warning("curentlyplaying.txt file not found")
        if line is None:
            return None
        pid, playlist = line.split(",")
        if pid == str(os.getpid()):
            logger.debug("same pid")
        else:
            logger.debug("old pid:" + str(os.getpid()))

        self.playlist = playlist
        self.current_state = AmpiController.RESTARTED
        if self.current_state == AmpiController.RESTARTED and self.playlist is not None:
            logger.info("Restarted. Previous Playlist: " + self.playlist)
            self.player = music_box.get_client(self.playlist)
            self.player.load_playlist(self.playlist)
        self.current_state = AmpiController.READY

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
            # self.player.close()
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
            if state == music_box.MusicBox.PLAYING:
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
        track = self.player.get_current_track()
        logger.debug("current track: %s", track)
        state = self.player.get_current_state()
        logger.debug("current state: %s", state)

    def back(self):
        if self.player is not None:
            self.player.back()
        logger.debug("Back")

    def fast_forward(self):
        logger.debug("Fast Forward 10 sec")

    def rewind(self):
        logger.debug("Rewind 10 sec")

    def pause(self):
        if self.player is not None:
            self.player.pause()
        logger.debug("Pause")

    def resume(self):
        if self.player is not None:
            self.player.resume()
        logger.debug("resume")

    def stop(self):
        if self.player is not None:
            self.player.stop()
        logger.debug("Stop")

    def mute(self):
        if self.player is not None:
            self.player.mute()
        logger.debug("Mute")

    def info(self):
        logger.debug("info")
        if self.player is not None:
            return self.player.get_current_track()

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
        else:
            logger.debug("Ampi Controller has received an unsuported event")


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
        ampi.start_deamon()
    else:
        pass
