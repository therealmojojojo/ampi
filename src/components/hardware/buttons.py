from gpiozero import Button
from components.model.event import AmpiEvent
import threading
import time
import logging
logger = logging.getLogger(__name__)


class ButtonsController(threading.Thread):
    NEXT_GPIO = 16
    PLAY_GPIO = 5
    BACK_GPIO = 26
    STOP_GPIO = 6
    RESET_GPIO = 22
    MUTE_GPIO = 13

    def __init__(self, event_handler):
        threading.Thread.__init__(self)
        self.event_handler = event_handler
        self.next = Button(self.NEXT_GPIO)
        self.play = Button(self.PLAY_GPIO)
        self.back = Button(self.BACK_GPIO)
        #self.stop = Button(self.STOP_GPIO)
        self.reset = Button(self.RESET_GPIO)
        self.mute = Button(self.MUTE_GPIO)
        self.running = True

    def exit_gracefully(self):
        self.running = False

    def stop_handler(self):
        self.event_handler(AmpiEvent.STOP_PRESSED)
        logger.debug("Stop pressed")

    def run(self):
        while self.running:
            try:
                if self.next.is_pressed:
                    self.event_handler(AmpiEvent.NEXT_PRESSED)
                    logger.debug("Next pressed")
                elif self.play.is_pressed:
                    logger.debug("Play pressed")
                    self.event_handler(AmpiEvent.PLAY_PRESSED)
                # elif self.stop.is_pressed:
                #    logger.debug("Stop pressed")
                #    self.event_handler(AmpiEvent.STOP_PRESSED)
                elif self.back.is_pressed:
                    logger.debug("Back pressed")
                    self.event_handler(AmpiEvent.BACK_PRESSED)
                elif self.reset.is_pressed:
                    logger.debug("Reset pressed")
                    self.event_handler(AmpiEvent.RESET_PRESSED)
                elif self.mute.is_pressed:
                    logger.debug("Mute pressed")
                    self.event_handler(AmpiEvent.MUTE_PRESSED)
            except BaseException as err:
                logger.error("Error handling button events: %s", err)
            time.sleep(.2)
        logger.info("Buttons Controller shut down!")
