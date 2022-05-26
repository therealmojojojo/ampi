from dotenv import load_dotenv, find_dotenv
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_MOPIDY_SERVER = "mopidy_server"
CONFIG_LOG_LEVEL = "log_level"


CONFIG_TEMP_FILES_FOLDER = "temp_files_folder"
CONFIG_DATABASE_FILE = "database_file"
CONFIG_ROON_ZONE = "roon_zone"
CONFIG_ROON_CORE_HOST = "roon_core_host"
CONFIG_ROON_CORE_PORT = "roon_core_port"
VALUE_ROON_CORE_ID_FILE = "roon_core_id_file"
VALUE_ROON_TOKEN_FILE = "roon_token_file"
CONFIG_MONITOR_FREQUENCY = "monitor_frequency"
CONFIG_USE_SCREEN = "use_screen"
CONFIG_USE_BUTTONS = "use_buttons"
CONFIG_USE_NFC = "use_nfc"

dotenv_path = find_dotenv()
print(dotenv_path)
load_dotenv(dotenv_path)


def get_property(name, default=None):
    logger.debug("Property requested: %s", name)
    property = os.environ.get(name)
    logger.debug("Found: %s", property)
    if property is None:
        return default
    return property
