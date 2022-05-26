from components.clients.roon import RoonClient
from components.clients.spotify import MopidySpotifyClient

import time
import logging
logger = logging.getLogger(__name__)
# factory


def get_client(playlist):
    logger.debug("Get Client for %s", playlist)
    clients = {
        "spotify": None,
        "roon": None
    }
    if playlist is None or playlist == '':
        return None
    if len(playlist) != 2:
        return None
    name = playlist[0]
    if name == "spotify":
        if clients[name] is None:
            clients[name] = MopidySpotifyClient(playlist[1])
    else:
        if clients[name] is None:
            clients[name] = RoonClient(playlist[1])

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
