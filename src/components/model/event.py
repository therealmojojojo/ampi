from enum import Enum


class AmpiEvent:
    CARD_READ = 0
    VOLUME_CHANGE = 1
#    VOLUME_DOWN = 2
    PLAY_PRESSED = 3
    STOP_PRESSED = 4
    NEXT_PRESSED = 5
    FFWD_PRESSED = 6
    FBWD_PRESSED = 7
    BACK_PRESSED = 8
    RESET_PRESSED = 9
    MUTE_PRESSED = 10
    TRACK_CHANGED = 11
    PLAYING_STATUS_CHANGED = 12
    UNEXPECTED_EVENT = -1