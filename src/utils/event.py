from enum import Enum


class AmpiEvent:
    CARD_READ = 0
    VOLUME_UP = 1
    VOLUME_DOWN = 2
    PLAY_PRESSED = 3
    STOP_PRESSED = 4
    NEXT_PRESSED = 5
    FFWD_PRESSED = 6
    FBWD_PRESSED = 7
    BACK_PRESSED = 8
    TURN_ONOFF = 9
    UNEXPECTED_EVENT = -1