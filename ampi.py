from enum import Enum
import time
from typing import Any
from components import nfc_cmd, music_box
from utils.event import AmpiEvent
import argparse

#volume
#screen
#switch
#status_led
#nfc_reader
import os




class AmpiController:
    #states
    NON_INITIALIZED = 0
    READY = 1 # not doing nothing, waiting for input
    PLAYING = 2 # playing a playlist
    PAUSED = 3 # was playing, now paused, waiting for interraction
    RESTARTED = 4
    current_state = NON_INITIALIZED
    component_registry = [];
    turn_on_off_state = 0;
    player = None
    playlist = None

    #saves pid & playslist on disk
    def save_state(self, playlist):
        with open('currentlyplaying.txt', 'w', encoding='utf-8') as f:
            f.write(str(os.getpid())+"," + playlist)

    def load_old_state(self):
        line = None
        try:
            with open('currentlyplaying.txt', 'r', encoding='utf-8') as f:
                line = f.readline()
        except FileNotFoundError:
            print("file not found")
        if line is None: 
            return None
        pid, playlist = line.split(",")
        if pid == str(os.getpid()): 
            print("same pid")
        else:
            print("old pid:" + str(os.getpid()))

        self.playlist = playlist
        self.current_state = AmpiController.RESTARTED
        

    def start(self):
        print("Running startup");
        global current_state, player
        current_state = AmpiController.READY
        self.load_old_state()
        if self.current_state == AmpiController.RESTARTED and self.playlist is not None:
            player = music_box.get_client(self.playlist)
            
        
    def turn_on_off(self):
        if( self.turn_on_off_state):
            self.turn_on_off_state = 0;
            print ("Turning off...");
        else:
            self.turn_on_off_state = 1;
            print ("Turning on...");
            
    def play(self, nfc_string: str):
        print(nfc_string)
        player = music_box.get_client(nfc_string)
        #if self.current_state == AmpiController.RESTARTED:   
        player.play_new()
        print("Start playing " + nfc_string);
        self.save_state(nfc_string)

    def volume_change(self):
        print("Volume changing");

    def next(self):
        player.next()
        print("Skip");
    
    def back(self):
        player.back()
        print("Back");
        
    def fast_forward(self):
        print("Fast Forward 10 sec");

    def rewind(self):
        print("Rewind 10 sec");

    def pause(self):
        player.pause()
        print("Pause");

    def resume(self):

        player.resume()
        print("resume");

    def stop(self):
        player.stop()
        print("Pause");
    
    def info(self):
        print("info");
        return player.get_current_track()

    def trigger_event(self, event: AmpiEvent, payload: Any):
        if event is None:
            return
        if     event == AmpiEvent.CARD_READ:
            print("Card Read event received, UID={}", payload)

        elif   event == AmpiEvent.VOLUME_UP:
            pass
        elif   event == AmpiEvent.VOLUME_DOWN:
            pass
        elif   event == AmpiEvent.PAUSE_PRESSED:
            pass
        elif   event == AmpiEvent.PLAY_PRESSED:
            pass
        elif   event == AmpiEvent.FFWD_PRESSED:
            pass
        elif   event == AmpiEvent.BACK_PRESSED:
            pass
        elif   event == AmpiEvent.TURN_ONOFF:
            pass
        else:
            print("Ampi Controller has received an unsuported event")

if __name__ == '__main__':
    ampi = AmpiController()
    ampi.start()
    parser = argparse.ArgumentParser(prog="ampi")
    parser.add_argument("-p", "--play", nargs="*", required=False)
    parser.add_argument("-a", "--action", choices=["stop", "next", "info", "pause", "resume"], nargs="*", required=False)
    args = parser.parse_args()
    config = vars(args)
    print(config)
    if config["play"] is not None:
        ampi.play(str(config["play"][0]))
    if config["action"] == "stop":
        ampi.pause()
    elif config["action"] == "next": 
        ampi.next()
    elif config["action"] == "info": 
        print(ampi.info())
    elif config["action"] == "pause": 
        ampi.pause()
    elif config["action"] == "resume": 
        ampi.resume()
    else:
        pass






   



    