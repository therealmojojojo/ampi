from enum import Enum
import time
from typing import Any
from components import nfc_cmd, music_box
from utils.event import AmpiEvent

#volume
#screen
#switch
#status_led
#nfc_reader


class AmpiController:
    #states
    NON_INITIALIZED = 0
    READY = 1 # not doing nothing, waiting for input
    PLAYING = 2 # playing a playlist
    PAUSED = 3 # was playing, now paused, waiting for interraction

    current_state = NON_INITIALIZED
    
    
    component_registry = [];
    turn_on_off_state = 0;

    def start(self):
        print("Running startup");
        global current_state
        current_state = AmpiController.READY
    
    def turn_on_off(self):
        if( self.turn_on_off_state):
            self.turn_on_off_state = 0;
            print ("Turning off...");
        else:
            self.turn_on_off_state = 1;
            print ("Turning on...");
            
    def play(self, nfc_string):
        print("Start playing " + nfc_string);

    def volume_change(self):
        print("Volume changing");

    def skip(self):
        print("Skip");
    
    def back(self):
        print("Back");
        
    def fast_forward(self):
        print("Fast Forward 10 sec");

    def rewind(self):
        print("Rewind 10 sec");

    def pause(self):
        print("Pause");

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
    ampi = AmpiController();
    ampi.start();
    while True:
        nfc_cmd.poll(ampi)
        time.sleep(1)



    