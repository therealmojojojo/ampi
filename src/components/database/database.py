from json import load
import utils
from utils import configuration
import utils.logger
import utils
import csv
import json
import logging
from components.hardware.nfc_cmd import NFCReader
import time
from components.clients.roon import SearchRoon

logger = logging.getLogger(__name__)

database = {
    "53  b1  1d  1b  00  05  80": {
        "album_url": "spotify:album:7z9NFSRufj49W9kaD2rORj",
        "album_title": ""
    },
}
database_file = configuration.get_property(
    configuration.CONFIG_DATABASE_FILE)
temp_files_folder = utils.configuration.get_property(
    configuration.CONFIG_TEMP_FILES_FOLDER)
database_file_path = temp_files_folder + "/" + database_file

initialized = False
path = database_file_path


def load_database(config_path=None):
    global database
    global path
    global initialized
    if initialized:
        return

    if config_path is None or config_path == '':
        #path = str(pathlib.Path(__file__).parent.resolve())
        path = database_file_path
    else:
        path = config_path
    logger.debug("Getting card database from %s", path)

    load_json_database(path)
    if database is None or len(database) == 0:
        logger.info("Empty database. Initializing...")
        database = {}
        return
    else:
        logger.info("Databased initialized and contains %d albums",
                    len(database))
    initialized = True


def load_csv_database(path):
    try:
        with open(path, mode='r') as infile:
            reader = csv.reader(infile)
            database = {rows[0]: rows[1] for rows in reader}
    except FileNotFoundError:
        logger.debug("Database file does not exist")
    return database


def load_json_database(path):
    global database
    try:
        with open(path, "r") as read_file:
            database = json.load(read_file)
    except Exception:
        logger.debug("Database file does not exist or wrong format")
        database = {}
    return database


def store_database():
    with open(path, "w") as write_file:
        json.dump(database, write_file, indent=4, sort_keys=True)


def get_playlist(cardUID):
    if not initialized:
        load_database()

    album = database.get(cardUID)
    if album is not None:
        logger.debug("Found album for card %s: %s %s", cardUID,
                     album["album_title"], album["album_url"])
        return (album["client"], album["album_url"])
    logger.debug("No album found for %s", cardUID)
    return None


def set_playlist(cardUID, album_title=None, album_url=None, client=None):
    if not initialized:
        load_database()
    album = {"album_title": album_title,
             "album_url": album_url, "client": client}
    if database.get(cardUID) is not None:
        logger.debug("Card already mapped to %s. Replacing", database[cardUID])
    database[cardUID] = album
    store_database()


""" 
def get_playlist(cardUID):
    global initialized
    if not initialized:
        load_database()
        initialized = True

    print("Searching for ", cardUID)
    try:
        return database[cardUID].strip()
    except:
        print('Card %s is not card list', cardUID)
        return None
 """


def get_valid_answer(message, valid_answer=None):
    answer = None
    while answer == None:
        answer = input(message)
        if valid_answer is not None and answer in valid_answer:
            break
        elif valid_answer is not None:
            print("Invalid choice. Again:  ")
            answer = None
        else:
            break
    return answer


def narrow_down(roon, query):
    found = False
    logger.debug("Initial search_string: %s", query)
    items = []
    tries = 0
    while not found:
        tries += 1
        if tries <= 2:
            items = roon.get_media(query, True)
        else:
            items = roon.get_media(query, False)
        if items is not None and len(items) == 1:
            found = True
            query.append(items[0]["title"])
            break
        if items is None or len(items) == 0:
            print("No items found")
            answer = get_valid_answer(
                "Your search?:  ", None)
            query.append(answer)
            continue
        valid_choice = []
        if len(items) > 1:
            print("Multiple entries found - choose one:")
            count = 1
            for item in items:
                print(count,
                      item["title"], item["subtitle"], item["item_key"])
                valid_choice.append(str(count))
                count += 1
            answer = get_valid_answer(
                "Your choice: ", valid_choice)
            logger.debug("search_string %s:", query)
            query.append(items[int(answer) - 1]["title"])
    logger.debug("Narrowed down search string: %s, %s",
                 query, items[0])
    return (query, items[0])


def get_roon_album():
    roon = SearchRoon()
    # roon.play_id("263:15")
    # return

    search_string = ["Library"]
    print("1. Composer")
    print("2. Artist")
    print("3. Playlist")
    answer = get_valid_answer(
        "Your choice (1/2/3)?:  ", ["1", "2", "3"])
    if answer == "1":
        # composer
        search_string.append("Composers")
        answer = get_valid_answer(
            "Composer string?:  ")

        search_string.append(answer)
        query = search_string.copy()
        (search_string, composer) = narrow_down(roon, query)

        # composition
        answer = get_valid_answer(
            "Composition string?:  ")

        search_string.append(answer)
        query = search_string.copy()
        (search_string, composition) = narrow_down(roon, query)

        # recording
        search_string.append("__all__")
        query = search_string.copy()
        (search_string, recording) = narrow_down(roon, query)

        # CD
        search_string.append("__all__")
        query = search_string.copy()
        (search_string, cd) = narrow_down(roon, query)

        logger.debug("%s %s %s %s %s", search_string,
                     composer, composition, recording, cd)
        title = recording["title"]
    elif answer == "2":
        logger.debug("Searching standard albums")
        search_string.append("Artists")
        answer = get_valid_answer(
            "Artist string?:  ")

        search_string.append(answer)
        query = search_string.copy()
        (search_string, artist) = narrow_down(roon, query)

        answer = get_valid_answer(
            "Album string?:  ")

        search_string.append(answer)
        query = search_string.copy()
        (search_string, album) = narrow_down(roon, query)

        title = album["title"]
        logger.debug("%s %s %s", search_string,
                     artist, album)
    else:
        search_string = ["Playlists"]
        search_string.append("__all__")
        query = search_string.copy()
        (search_string, playlist) = narrow_down(roon, query)
        title = playlist["title"]
        logger.debug("%s %s", search_string,
                     playlist)

    return (title, search_string, "roon")


def get_spotify_album():
    pass


def collect_new_card_info():
    answer = get_valid_answer(
        "Do you want to add a new card (Y/n)?", ["Y", "n"])
    if answer == "n":
        logger.debug("Nothing to do")
        return
    answer = get_valid_answer(
        "1. Roon or 2. Spotify [not supported since 16.05.2022] (1/2)?", ["1"])
    if answer != "1":
        logger.debug("Adding spotify album")
        return get_spotify_album()
    else:
        logger.debug("Adding Roon album")
        return get_roon_album()


def process_new_card(event_id, cardUID):
    logger.debug("new card received %s", cardUID)
    album = get_playlist(cardUID)
    if album is None:
        logger.debug("no album in library")
    else:
        logger.debug("Found album %s", album)
    (title, search_string, client) = collect_new_card_info()
    set_playlist(cardUID, title, search_string, client)


if __name__ == '__main__':
    # init logging
    if (not utils.logger.setup_logging(console_log_output="stdout", console_log_level="debug", console_log_color=True,
        logfile_file="ampi.log", logfile_log_level="debug", logfile_log_color=False, logfile_log_datefmt='%Y/%m/%d %I:%M:%S %p',
                                       log_line_template="%(color_on)s[%(asctime)s ] [%(threadName)s] [%(levelname)-8s] [%(filename)s] [%(funcName)s] [%(lineno)d] %(message)s%(color_off)s")):
        logger.debug("Failed to setup logging.")
        exit(1)
    logger = logging.getLogger(__name__)
    log_level = configuration.get_property(
        configuration.CONFIG_LOG_LEVEL)
    nfc_reader = NFCReader(process_new_card)
    nfc_reader.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        nfc_reader.exit_gracefully()
        logger.debug(database)
