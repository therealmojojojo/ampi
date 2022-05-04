import logging
logger = logging.getLogger(__name__)


class MusicBox:

    UNKNOWN_PLAYING_STATE = -1
    PLAYING = 0
    STOPPED = 1
    PAUSED = 2

    def __init__(self):
        self.current_playlist = None
        self.server = None

    def load_playlist(self, playlist=None):
        pass

    def resume(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def next(self):
        pass

    def back(self):
        pass

    def play(self):
        pass

    def clear(self):
        pass

    def mute(self):
        pass

    def volume_change(self, volume=40):
        pass

    def get_current_state(self):
        pass

    def get_current_track(self):
        pass

    def get_current_time(self):
        pass

    def get_current(self):
        pass

    def connect_to_provider(self):
        logger.debug("super")
        pass

    def close():
        logger.debug("closing")
        pass


class TrackMetadata:
    track_number = 1
    track_name = None
    composer_name = None
    artist_name = None
    album_name = None
    album_year = None
    disk_number = 1
    total_disks = 1
    bitrate = 100

    def __init__(self):
        pass
