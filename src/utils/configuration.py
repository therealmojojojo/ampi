from dotenv import load_dotenv, find_dotenv
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_MOPIDY_SERVER = "mopidy_server"
CONFIG_LOG_LEVEL = "log_level"

dotenv_path = find_dotenv()
print(dotenv_path)
load_dotenv(dotenv_path)

def get_property(name):
    logger.debug("Property requested: %s", name)
    property = os.environ.get(name)
    logger.debug("Found: %s", property)
    return property  