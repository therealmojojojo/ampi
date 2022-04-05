import signal                   
import sys
import time
import RPi.GPIO as GPIO
import components
from components import nfc_reader

#volume
#screen
#switch
#status_led
#nfc_reader

class AmpiController:
    component_registry = [];
    turn_on_off_state = 0;

    def start():
        nfc_reader.setup()

        print("Running setup");
    
    def turn_on_off(self):
        if( self.turn_on_off_state):
            self.turn_on_off_state = 0;
            print ("Turning off...");
        else:
            self.turn_on_off_state = 1;
            print ("Turning on...");
            
    def play(self, nfc_string):
        print("Start playing" + nfc_string);

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



if __name__ == '__main__':
    
    ampi = AmpiController();
    ampi.start();
    while True:
        nfc_reader.loop()



    