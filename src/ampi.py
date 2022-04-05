import signal                   
import sys
import time
import RPi.GPIO as GPIO

#volume
#screen
#switch
#status_led
#nfc_reader

class AmpiController:
    component_registry = [];
    turn_on_off_state = 0;

    def setup():
        print("Running setup");
    
    def turn_on_off(self):
        if( self.turn_on_off_state):
            self.turn_on_off_state = 0;
            print ("Turning off...");
        else:
            self.turn_on_off_state = 1;
            print ("Turning on...");
            
    def play(self):
        print("Start playing");

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
    GPIO.setmode(GPIO.BCM)

    ampi = AmpiController();
    ampi.setup();
    ampi.turn_on_off();



    