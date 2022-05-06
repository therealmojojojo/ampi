#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
from components.model.musicbox import TrackMetadata
from waveshare import epd2in9
from utils import logger
import math
logger = logging.getLogger(__name__)

# picdir = os.path.join(os.path.dirname(
#    os.path.dirname(os.path.realpath(__file__))), 'img')
# libdir = os.path.join(os.path.dirname(
#    os.path.dirname(os.path.realpath(__file__))), 'lib')

picdir = "/home/pi/Apps/ampi/img/"
fontType = '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'


class EpdDisplay:
    format = {
        "track_name": {
            "total_chars": 13, "font_size": 38,
            "total_chars2": 17, "font_size2": 28,
        },
        "album_name": {
            "total_chars": 17, "font_size": 28,
            "total_chars2": 21, "font_size2": 24,
        },
        "artist_name": {
            "total_chars": 17, "font_size": 28,
            "total_chars2": 21, "font_size2": 24,
        }
    }

# Oversize message handling
    TRUNCATE = 0
    SCROLL = 1
    WRAP = 2

    oversize = WRAP

    height = 0
    width = 0
    line_fill = 255
    char_fill = 0

    total_lines = 3
    padding = 7

    # Scroll buffer
    LineBuffer = []
    BufferIndex = []

    def __init__(self):
        self.epd = epd2in9.EPD()
        logger.info("init and Clear")
        # Create line frame
        # 255: clear the frame
        self.frame = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.frame)
        self.clear()

        # self.font = ImageFont.truetype(fontType, self.font_size)
        # Create scroll line buffers
        for i in range(0, self.total_lines):
            self.LineBuffer.append(["", 0])
            self.BufferIndex.append(0)

        self.oversize = self.WRAP

    def clear(self):
        self.frame = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.frame)
        self.epd.init(self.epd.lut_full_update)
        self.epd.Clear(0xFF)
    '''
    def draw(self, buffer=[]):
        i = 0
        for line in buffer:
            self.draw.text((10, 0), line, font=self.font, fill=0)
            i += 1

        self.epd.display(self.epd.getbuffer(self.draw))
    '''
    # Top display routine

    def out(self, line_number, text):
        if len(text) > self.total_chars:

            if self.oversize == self.SCROLL:
                self._scroll(line_number, text)

            elif self.oversize == self.WRAP:
                self._wrap(line_number, text)
                self.BufferIndex[line_number-1] += 1  # DEBUG

            else:
                self._out(line_number, text[:self.total_chars])
        else:
            self._out(line_number, text)
        return

    # Text out
    def _out(self, line_number, text="", font_size=24):
        self.LineBuffer[line_number-1] = [text, font_size]
        return
    '''
    def _wrap(self, line_number, text=""):
        self.LineBuffer[line_number-1] = text[:self.total_chars]
        self.LineBuffer[line_number] = text[self.total_chars:]
        return
    '''
    # Set oversize text behaviour

    def setWrap(self, mode):
        if mode >= self.TRUNCATE and mode <= self.WRAP:
            self.oversize = mode

    # Update the display
    def update(self):
        # Write text to lines
        line_height = 0
        for i in range(0, self.total_lines):
            text, font_size = self.LineBuffer[i]
            print(text, len(text), font_size)
            if len(text) > 0 or self.BufferIndex[i] > 0:
                line_number = i+1
                image_width, image_height = self.frame.size
                print(image_width, image_height)
                # self.draw.rectangle((0, 0, image_width, image_height),
                #                    fill=self.line_fill)

                self.draw.text((10, line_height), text, font=self.get_font(font_size),
                               fill=self.char_fill)
                line_height += font_size + self.padding
        # add media controls
        media = Image.open(os.path.join(picdir, 'mediabuttons.bmp'))
        self.frame.paste(media, (20, 110))
        # Update screen
        self.epd.display(self.epd.getbuffer(self.frame))

    # Scroll text
    def _scroll(self, line_number, text=""):
        sText = text[self.BufferIndex[line_number-1]:]
        self._out(line_number, sText)
        fSize = self.font.getsize(sText)
        if fSize[0] > self.height:
            self.BufferIndex[line_number-1] += 1
        else:
            self.BufferIndex[line_number-1] = 0
        return

    def sleep(self):
        self.epd.sleep()

    # Reverse screen colour
    def reverse(self, truefalse):
        if truefalse:
            self.line_fill = 0
            self.char_fill = 255
        else:
            self.line_fill = 255
            self.char_fill = 0

    def center_text(self, text, nr_chars):
        logger.debug("nr_chars=%d, text %s", nr_chars, text)

        if len(text) < nr_chars:
            nr_space_chars = math.floor((nr_chars - len(text))/2)
            text = " " * nr_space_chars + text + " " * nr_space_chars
        return text

    def _parse_metadata_name(self, meta_name, meta_value):
        # split after : - for classical music tracks
        if meta_value is not None:
            if meta_name == "track_name":
                parts = meta_value.split(':')
                meta_value = parts[len(parts) - 1].strip()
        else:
            meta_value = ""

        if len(meta_value) > self.format[meta_name]["total_chars"]:
            meta_font_size = self.format[meta_name]["font_size2"]
            if len(meta_value) > self.format[meta_name]["total_chars2"]:
                meta_value = meta_value[0:self.format[meta_name]
                                        ["total_chars2"]]

            meta_value = self.center_text(
                meta_value, self.format[meta_name]["total_chars2"])
        else:
            meta_font_size = self.format[meta_name]["font_size"]
            meta_value = self.center_text(
                meta_value, self.format[meta_name]["total_chars"])

        return meta_value, meta_font_size

    def refresh(self, track_metadata):
        track_name, track_font_size = self._parse_metadata_name("track_name",
                                                                track_metadata.track_name)
        album_name, album_font_size = self._parse_metadata_name("album_name",
                                                                track_metadata.album_name)
        artist_name, artist_font_size = self._parse_metadata_name("artist_name",
                                                                  track_metadata.artist_name)
        self._out(1, track_name, track_font_size)
        self._out(2, album_name, album_font_size)
        self._out(3, artist_name, artist_font_size)

    def get_font(self, font_size):
        return ImageFont.truetype(fontType, font_size)


if __name__ == "__main__":
    logger.info("start")
    import time
    import datetime
    epd = EpdDisplay()
    epd.setWrap(epd.WRAP)
    epd.reverse(False)
    epd.clear()
    volume = 90
    try:
        while True:

            track_metadata = TrackMetadata()
            track_metadata.album_name = "Tchaikovsky: Piano Concerto No.1"
            track_metadata.track_name = "Piano Concerto No. 1 in B-Flat Minor, Op. 23, TH. 55: 1. Allegro non troppo e molto maestoso - Allegro con spirito - Live at Philharmonie, Berlin"
            track_metadata.artist_name = "Herbert von Karajan, Pyotr Ilyich Tchaikovsky"

            epd.refresh(track_metadata)
            epd.update()

            time.sleep(5)
            epd.clear()
            track_metadata.album_name = "A Moon Shaped Pool"
            track_metadata.track_name = "Burn The Witch"
            track_metadata.artist_name = "Radiohead"
            epd.refresh(track_metadata)
            epd.update()

            time.sleep(5)
            epd.clear()
            track_metadata.album_name = "Bach: Fugues"
            track_metadata.track_name = "The Well-Tempered Clavier (24), collection of preludes & fugues, Book I, BWV 846-869 (BC L80-103): Fuga I a 4 voci, BWV 846"
            track_metadata.artist_name = "Emerson String Quartet / Johann Sebastian Bach / Emanuel Aloys Förster"
            epd.refresh(track_metadata)
            epd.update()

            time.sleep(5)
            epd.clear()

            epd._out(1, "01234567890123456789", 38)
            epd._out(2, "01234567890123456789", 28)
            epd._out(3, "01234567890123456789012345678", 24)
            epd.update()

            time.sleep(5)

            # epd.clear()
            break

    except KeyboardInterrupt:
        print("\nExit")
        epd.sleep()
        sys.exit(0)
