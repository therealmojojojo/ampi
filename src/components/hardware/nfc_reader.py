import time
import binascii

from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c

PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)
ampi_controller = None

def setup(ampi):
    i = 0
    while i < 3:
        try: 
            print("nfc begin {}", i)
            nfc.begin()
            break
        except OSError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("nfc.begin failure: ", e.args)
            time.sleep(1)
            i = i + 1
    global ampi_controller 
    ampi_controller = ampi

    # initialising the NFC card
    i = 0
    while i < 3:
        try: 
            print("nfc getFirmwareVersion {}", i)
            versiondata = nfc.getFirmwareVersion()
            break
        except OSError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("nfc.getFirmwareVersion failure: ", e.args)
            time.sleep(1)
            i = i + 1
    if not versiondata:
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    # Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))
    # Set the max number of retry attempts to read from a card
    # This prevents us from waiting forever for a card, which is
    # the default behaviour of the pn532.
    i = 0
    while i < 3:
        try:
            print("nfc setPassiveActivationRetries {}", i)
            nfc.setPassiveActivationRetries(0xFF)

            # configure board to read RFID tags
            nfc.SAMConfig()
            break
        except OSError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("Reading from DHT failure: ", e.args)
            time.sleep(1)
            i = i + 1
    print("Waiting for an ISO14443A card")

        

def loop():
    # Wait for an ISO14443A type cards (Mifare, etc.).  When one is found
    # 'uid' will be populated with the UID, and uidLength will indicate
    # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    i = 0
    success = False
    uid = 0
    while i < 3:
        try:
            print("nfc readPassiveTargetID {}", i)
            success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)
        except OSError as e:
            # Reading doesn't always work! Just print error and we'll try again
            print("nfc.readPassiveTargetID failure: ", e.args)
            time.sleep(1)
            i = i + 1
    if (success):
        print("Found a card!")
        print("UID Length: {:d}".format(len(uid)))
        print("UID Value: {}".format(binascii.hexlify(uid)))
        print("Raw UID:{}", uid)
        # Wait 1 second before continuing
        time.sleep(1)
        ampi_controller.play(binascii.hexlify(uid))
        return True
    else:
        # pn532 probably timed out waiting for a card
        print("Timed out waiting for a card")
        time.sleep(1)
        return False


if __name__ == '__main__':
    setup()
    found = loop()
    while not found:
      found = loop()