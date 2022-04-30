import os
import time

import logging
logger = logging.getLogger(__name__)

import jsonrpclib

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

class RoonClient(MusicBox):
    pass
#https://github.com/flandrefinish/mopidycli/blob/master/mopidycli/cli.py
class MopidySpotifyClient(MusicBox):
    def __init__(self, playlist):
        self.current_playlist = playlist
        self.server = jsonrpclib.Server(os.environ.get("mopidy_server") + "/mopidy/rpc")
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
        logger.debug('Got hits from browse(): %r', hits)
        if len(hits) == 0:
            logger.debug("Nothing found for playlist", self.current_playlist)
            return 0
        self.server.core.tracklist.clear()
        self.server.core.tracklist.add(uris=[t['uri'] for t in hits])

    def get_current_track(self):
        return self.server.core.playback.get_current_track()

    def next(self):
        self.server.core.playback.next()
        #sometimes mopidy does not play 
        self.play()

    def play(self):
        self.server.core.playback.play()
    
    def back(self):
        self.server.core.playback.previous()
        #sometimes mopidy does not play 
        self.play()

    def pause(self):
        self.server.core.playback.pause()

    def resume(self):
        self.server.core.playback.resume()

    def play(self):
        self.server.core.playback.play()

    def stop(self):
        self.server.core.playback.stop()
    
    def clear(self):
        self.server.core.tracklist.clear()

#factory
def get_client(playlist: str):
    logger.debug("Get Client for %s", playlist)
    clients = {
        "Spotify": None,
        "Roon": None
    }
    if playlist is None or playlist == '':
        return None 
    else:
        name = "Spotify" if playlist.find("spotify") >= 0 else "Roon"
    if name == "Spotify":
        if clients[name] is None:
            clients[name] = MopidySpotifyClient(playlist)
    else:
        if clients[name] is None:
            clients[name] = RoonClient()
            return None
    
    logger.debug (clients[name])
    return clients[name]

if __name__ == "__main__":
    logger.debug("----- getting spotify -------")
    player = get_client("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    state = player.get_current_state()
    logger.debug("current state: ", state)
    logger.debug("----- play album -------")
    player.load_playlist("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    player.play()
    time.sleep(5)
    state = player.get_current_state()
    logger.debug("current state: ", state)
    track = player.get_current_track()
    logger.debug("current track: ", track)
    logger.debug("----- next -------")
    player.next()
    time.sleep(10)
    state = player.get_current_state()
    logger.debug("current state: ", state)
    track = player.get_current_track()
    logger.debug("current track: ", track)
    logger.debug("----- previous -------")
    player.back()
    time.sleep(10)
    state = player.get_current_state()
    logger.debug("current state: ", state)
    track = player.get_current_track()
    logger.debug("current track: ", track)                                        
