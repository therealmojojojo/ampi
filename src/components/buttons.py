from gpiozero import Button 
from signal import pause
from utils.event import AmpiEvent
import threading
import time

class ButtonsController(threading.Thread):
    NEXT_GPIO = 16
    PLAY_GPIO = 6
    #BACK_GPIO = 16
    #NEXT_GPIO = 6

    def __init__(self, event_handler):
        threading.Thread.__init__(self)
        self.event_handler = event_handler
        self.next = Button(self.NEXT_GPIO)

    def stop_handler(self):
        self.event_handler(AmpiEvent.STOP_PRESSED)
        print("Stop pressed")

    def run(self):
        while True:
            if self.next.is_pressed:
                self.event_handler(AmpiEvent.NEXT_PRESSED)
                print("Next pressed")
            time.sleep(.2)
