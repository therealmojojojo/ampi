# https://github.com/flandrefinish/mopidycli/blob/master/mopidycli/cli.py
from components.model.musicbox import MusicBox, TrackMetadata
import jsonrpclib
import os
import time
import logging
import json

logger = logging.getLogger(__name__)


class MopidySpotifyClient(MusicBox):
    def __init__(self, playlist):
        self.current_playlist = playlist
        self.server = jsonrpclib.Server(
            os.environ.get("mopidy_server") + "/mopidy/rpc")
        logger.debug(self.server)
        self.load_playlist(playlist)

    def get_current_state(self):
        state = self.server.core.playback.get_state()
        if state == "playing":
            return MusicBox.PLAYING
        elif state == "stopped":
            return MusicBox.STOPPED
        elif state == "paused":
            return MusicBox.PAUSED
        return MusicBox.UNKNOWN_PLAYING_STATE

    def load_playlist(self, playlist=None):

        if playlist is not None:
            self.current_playlist = playlist
            logger.debug("Loading playlist: " + playlist)
        else:
            logger.error("Playlist is empty")
            return
        hits = self.server.core.library.browse(self.current_playlist)
        # browse(): Returns a list of mopidy.models.Ref objects for the directories and tracks at the given uri.
        logger.debug('Got hits from browse(): %r',
                     json.dumps(hits, sort_keys=True, indent=4))
        if len(hits) == 0:
            logger.debug("Nothing found for playlist", self.current_playlist)
            return 0
        self.server.core.tracklist.clear()
        self.server.core.tracklist.add(uris=[t['uri'] for t in hits])

    def get_current_track(self):
        track = TrackMetadata()
        current_track = self.server.core.playback.get_current_track()
        if current_track is not None:
            track.track_name = current_track["name"]
            track.album_year = current_track["date"]
            track.track_number = current_track["track_no"]
            album = current_track["album"]
            track.album_name = album["name"]
            artists = current_track["artists"]
            i = 1
            for artist in artists:
                if i >= 3:
                    break
                if track.artist_name is not None:
                    track.artist_name = track.artist_name + \
                        ", " + artist["name"]
                else:
                    track.artist_name = artist["name"]
                i += 1

        return track

    def next(self):
        self.server.core.playback.next()
        # sometimes mopidy does not play
        self.play()

    def play(self):
        self.server.core.playback.play()
        time.sleep(0.5)
        logger.debug("playing %s", self.get_current_track())

    def back(self):
        self.server.core.playback.previous()
        # sometimes mopidy does not play
        self.play()

    def pause(self):
        self.server.core.playback.pause()

    def resume(self):
        self.server.core.playback.resume()

    def stop(self):
        self.server.core.playback.stop()

    def clear(self):
        self.server.core.tracklist.clear()

    def mute(self):
        mute_status = self.server.core.mixer.get_mute()
        logger.debug("Current mute status %d", mute_status)
        self.server.core.mixer.set_mute(not mute_status)

    def volume_change(self, volume=40):
        self.server.core.mixer.set_volume(volume)
