from components.model.musicbox import MusicBox, TrackMetadata
from pyroon.roonapi.roonapi import RoonApi
from pyroon.roonapi.discovery import RoonDiscovery

import time
import logging
import json
import utils.configuration
from utils import logger
logger = logging.getLogger(__name__)

appinfo = {
    "extension_id": "Ampi",
    "display_name": "Raspberry NFC Player for Roon",
    "display_version": "1.0.0",
    "publisher": "costin",
    "email": "costin.genescu@gmail.com",
}

temp_files_folder = utils.configuration.get_property(
    utils.configuration.CONFIG_TEMP_FILES_FOLDER)
core_file = temp_files_folder + "/" + utils.configuration.VALUE_ROON_CORE_ID_FILE
token_file = temp_files_folder + "/" + utils.configuration.VALUE_ROON_TOKEN_FILE
core_host = utils.configuration.get_property(
    utils.configuration.CONFIG_ROON_CORE_HOST)
core_port = utils.configuration.get_property(
    utils.configuration.CONFIG_ROON_CORE_PORT)
target_zone = utils.configuration.get_property(
    utils.configuration.CONFIG_ROON_ZONE)


class RoonClient(MusicBox):

    def __init__(self, playlist):
        self.current_playlist = playlist
        self.api = None
        self.zone_id = None

        try:
            self.core_id = open(core_file).read()
            self.token = open(token_file).read()
            logger.debug("core_id, token: %s, %s ", self.core_id, self.token)
            self.api = RoonApi(appinfo, self.token, core_host, core_port, True)
        except OSError:
            logger.warning("Not authorized yet. Authorizing")
            self.api = self.authorize()
        if self.api is None:
            logger.error("Roon connection failed")
            return
        logger.debug("Connection established : %s", self.api)
        zones = self.api.zones
        logger.debug("Zones : ", zones)
        for output in zones.values():
            logger.debug("target_zone : %s", target_zone)
            if output["display_name"] == target_zone:
                logger.debug("Output : %s", output["display_name"])
                self.zone_id = output["zone_id"]

        if not self.zone_id:
            logger.error("Zone not found")
            return
        logger.debug("playing on zone: %s, output_id=%s",
                     target_zone, self.zone_id)
        # self.load_playlist(self.current_playlist)

    def load_playlist(self, playlist=None):
        logger.debug("playing playlist %s", playlist)
        self.api.play_media(self.output_id, playlist, action="Pause")

    def resume(self):
        self.api.playback_control(self, self.zone_id, control="play")

    def stop(self):
        self.api.playback_control(self, self.zone_id, control="stop")

    def pause(self):
        self.api.playback_control(self, self.zone_id, control="pause")

    def next(self):
        self.api.playback_control(self, self.zone_id, control="next")

    def back(self):
        self.api.playback_control(self, self.zone_id, control="previous")

    def play(self):
        self.api.playback_control(self, self.zone_id, control="play")

    def clear(self):
        pass

    def mute(self):
        pass

    def volume_change(self, volume=40):
        pass

    def get_current_state(self):
        pass

    def get_current_track(self):
        zone = self.api.zone_by_name(target_zone)
        track_info = TrackMetadata()
        if zone is not None:
            logger.debug("\nNow playing in zone: %s", target_zone)
            zone_dump = json.dumps(zone).encode("utf8")
            logger.debug("\Zone:\t %s", zone_dump.decode())
            track = json.dumps(zone["now_playing"]["three_line"]
                               ["line1"], ensure_ascii=False).encode('utf8')
            logger.debug("\tTrack:\t %s", track.decode())
            artist = json.dumps(
                zone["now_playing"]["three_line"]["line2"], ensure_ascii=False).encode('utf8')
            logger.debug("\tArtist:\t %s", artist.decode())
            album = json.dumps(zone["now_playing"]["three_line"]
                               ["line3"], ensure_ascii=False).encode('utf8')
            logger.debug("\tAlbum:\t %s", album.decode())

            track_info.track_name = track.decode()
            track_info.album_name = album.decode()
            track_info.artist_name = artist.decode()
        else:
            logger.debug("Invalid output_id %s", self.zone_id)
        return track_info

    def get_current_time(self):
        pass

    def get_current(self):
        pass

    def connect_to_provider(self):
        logger.debug("super")
        pass

    def close(self):
        logger.debug("closing")
        if self.api is not None:
            self.api.close()

    def authorize(self):
        api = RoonApi(appinfo, None, core_host, core_port, False)
        auth_api = []
        while len(auth_api) == 0:
            print("Waiting for authorisation")
            time.sleep(1)
            if api.token is not None:
                auth_api = [api]

        api = auth_api[0]

        print("Got authorisation")
        print(api.host)
        print(api.core_name)
        print(api.core_id)

        # This is what we need to reconnect
        self.core_id = api.core_id
        self.token = api.token

        with open(core_file, "w") as f:
            f.write(api.core_id)
        with open(token_file, "w") as f:
            f.write(api.token)

        return api


if __name__ == "__main__":
    utils.logger.main()
    client = RoonClient(None)
    client.api.play_media(client.zone_id,
                          ["Library", "Albums", "Bach: Fugues"])
    logger.debug(vars(client.get_current_track()))
