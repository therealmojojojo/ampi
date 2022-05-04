from components.clients.roon import RoonClient
from components.clients.spotify import MopidySpotifyClient

import time
import logging
logger = logging.getLogger(__name__)
# factory


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

    logger.debug(clients[name])
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
