import RPi.GPIO as GPIO
import threading
import time
from math import floor
from gpiozero import RotaryEncoder
from utils.event import AmpiEvent
import alsaaudio
import logging
logger = logging.getLogger(__name__)


class VolumeControl(threading.Thread):
    # GPIO Ports
    GPIO_A = 12  # CLK
    GPIO_B = 27
    INIT_VOLUME = 40

    def rotated_event(self):
        volume = floor((-self.rotor.value + 1)*50)
        #self.event_handler(AmpiEvent.VOLUME_CHANGE, volume)
        try:
            lc, rc = self.mixer.getvolume()
            logger.debug("Current AlsaMixer volume: %d, %d", lc, rc)
            if volume < 0:
                self.mixer.setvolume(0)
            elif volume > 80:
                self.mixer.setvolume(80)
            else:
                self.mixer.setvolume(volume)
        except:
            logger.error("Cannot set volume via AlsaMixer")

    def __init__(self, event_handler):
        threading.Thread.__init__(self)
        self.event_handler = event_handler
        self.running = True
        self.rotor = RotaryEncoder(
            VolumeControl.GPIO_A, VolumeControl.GPIO_B, max_steps=20, bounce_time=0.1)
        self.rotor.value = 0
        self.rotor.when_rotated = self.rotated_event
        try:
            self.mixer = alsaaudio.Mixer("Digital")
        except:
            logger.warning("Could not set Alsa mixer")
        if self.mixer is not None:
            logger.debug("Alsa mixer set")
            self.set_init_volume()

    def set_init_volume(self):
        try:
            lc, rc = self.mixer.getvolume()
            logger.debug("Current AlsaMixer volume: %d, %d", lc, rc)
            self.mixer.setvolume(VolumeControl.INIT_VOLUME)
            self.rotor.value = VolumeControl.INIT_VOLUME/50 - 1
        except:
            logger.error("Cannot set volume via AlsaMixer")

    def run(self):
        while self.running:
            time.sleep(1)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    volume_control = VolumeControl(None)
    volume_control.start()
    while True:
        print(volume_control.rotor.value, "->",
              floor((-volume_control.rotor.value + 1)*50))
        time.sleep(0.2)
