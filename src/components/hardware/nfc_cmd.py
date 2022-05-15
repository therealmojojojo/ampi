import subprocess
from components.model.event import AmpiEvent
import threading
import logging
logger = logging.getLogger(__name__)


class NFCReader(threading.Thread):
    def __init__(self, event_handler):
        threading.Thread.__init__(self)
        self.event_handler = event_handler
        self.running = True

    def exit_gracefully(self):
        self.running = False
        try:
            if self.process is not None:
                self.process.terminate()
        except Exception:
            logger.error("Exception terminating the nfc process")

    def run(self):
        while self.running:
            self.process = subprocess.Popen(['nfc-poll'],
                                            stdout=subprocess.PIPE,
                                            universal_newlines=True)
            output = self.process.stdout.readline()
            for output in self.process.stdout.readlines():
                line = output.strip()
                logger.debug(line)
                if line.startswith("UID"):
                    uid = line.split(":")[1].strip()
                    if self.event_handler is not None and self.running:
                        self.event_handler(AmpiEvent.CARD_READ, uid)
                    else:
                        logger.debug("UID = " + uid)
            # Do something else

            return_code = self.process.poll()

            if return_code is not None and self.running:
                if return_code == 0:
                    continue
                logger.debug('nfc-poll RETURN CODE {}', return_code)
                # Process has finished, read rest of the output
                self.event_handler(AmpiEvent.UNEXPECTED_EVENT)
                break
        logger.info("Shutting down NFC Reader")
