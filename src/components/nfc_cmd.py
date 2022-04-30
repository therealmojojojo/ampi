import subprocess
from utils.event import AmpiEvent
import threading
import logging
logger = logging.getLogger(__name__)

class NFCReader(threading.Thread):
    def __init__(self, event_handler):
        threading.Thread.__init__(self)
        self.event_handler = event_handler

    def run(self):
        while True:
            process = subprocess.Popen(['nfc-poll'], 
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
            output = process.stdout.readline()
            for output in process.stdout.readlines():
                line = output.strip()
                if line.startswith("UID"):
                    uid = line.split(":")[1].strip()
                    if self.event_handler is not None:
                        self.event_handler(AmpiEvent.CARD_READ, uid)
                    else:
                        logger.debug("UID = " + uid)
            # Do something else

            return_code = process.poll()

            if return_code is not None:
                if return_code == 0:
                    continue
                logger.debug('nfc-poll RETURN CODE {}', return_code)
                # Process has finished, read rest of the output 
                self.event_handler(AmpiEvent.UNEXPECTED_EVENT)
                break