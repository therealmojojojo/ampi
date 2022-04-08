from enum import Enum


class AmpiEvent (Enum):
    CARD_READ = 0
    VOLUME_UP = 1
    VOLUME_DOWN = 2
    PAUSE_PRESSED = 3
    PLAY_PRESSED = 4
    FFWD_PRESSED = 5
    BACK_PRESSED = 6
    TURN_ONOFF = 7