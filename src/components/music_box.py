import os
import time
import json
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
print(dotenv_path)
load_dotenv(dotenv_path)

print(os.environ.get("PYTHONPATH"))
print(os.environ.get("mopidy_server"))

import requests
from mopidy import core

import jsonrpclib

class MusicBox:
    
    def __init__(self):
        self.current_playlist = None
        self.server = None

    def play_new(self, playlist: str):
        
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
        print("super")
        pass

class RoonClient(MusicBox):
    pass
#https://github.com/flandrefinish/mopidycli/blob/master/mopidycli/cli.py
class MopidySpotifyClient(MusicBox):
    def __init__(self, playlist):
        self.current_playlist = playlist
        self.server = jsonrpclib.Server(os.environ.get("mopidy_server") + "/mopidy/rpc")
        print(self.server)

    def get_current_state(self):
        state = self.server.core.playback.get_state()
        return state

    def play_new(self):  
        hits = self.server.core.library.browse(self.current_playlist)
        # browse(): Returns a list of mopidy.models.Ref objects for the directories and tracks at the given uri.
        print('Got hits from browse(): %r', hits)
        if len(hits) == 0:
            print("Nothing found for playlist", self.current_playlist)
            return 0
        self.server.core.tracklist.clear()
        self.server.core.tracklist.add(uris=[t['uri'] for t in hits])
        self.server.core.playback.play()

    def get_current_track(self):
        return self.server.core.playback.get_current_track()

    def next(self):
        self.server.core.playback.next()

    def back(self):
        self.server.core.playback.previous()

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
    print("Get Client for " + playlist)
    clients = {
        "Spotify": MopidySpotifyClient,
        "Roon": RoonClient
    }
    if playlist is None or playlist == '':
        return None 
    else:
        name = "Spotify" if playlist.find("spotify") >= 0 else "Roon"
    print (clients[name])
    return clients[name](playlist)


if __name__ == "__main__":
    print("----- getting spotify -------")
    player = get_client("spotify")
    player.connect_to_provider()
    state = player.get_current_state()
    print("current state: ", state)
    print("----- play album -------")
    player.play_new("spotify:album:1sKj6LEXiEfCmsiKwPy5uG")
    time.sleep(5)
    state = player.get_current_state()
    print("current state: ", state)
    track = player.get_current_track()
    print("current track: ", track)
    print("----- next -------")
    player.next()
    time.sleep(10)
    state = player.get_current_state()
    print("current state: ", state)
    track = player.get_current_track()
    print("current track: ", track)
    print("----- previous -------")
    player.back()
    time.sleep(10)
    state = player.get_current_state()
    print("current state: ", state)
    track = player.get_current_track()
    print("current track: ", track)                                        
