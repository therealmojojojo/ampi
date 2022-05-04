#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import logging
import time
import traceback
from PIL import Image, ImageDraw, ImageFont
from lib.waveshare import epd2in9

# picdir = os.path.join(os.path.dirname(
#    os.path.dirname(os.path.realpath(__file__))), 'img')
libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')

picdir = "/home/pi/Apps/ampi/img/"
fontType = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

if os.path.exists(libdir):
    sys.path.append(libdir)


logging.basicConfig(level=logging.DEBUG)

font24 = ImageFont.truetype(fontType, 24)
font18 = ImageFont.truetype(fontType, 18)


class EpdDisplay:
    total_lines24 = 5
    total_lines18 = 5
    total_chars24 = 20
    total_chars18 = 25

    buttons = "  <<    []   II/>   >>   "
# Oversize message handling
    TRUNCATE = 0
    SCROLL = 1
    WRAP = 2

    oversize = WRAP

    height = 0
    width = 0
    line_fill = 255
    char_fill = 0
    font_size = 24
    total_lines = total_lines24
    total_chars = total_chars24
    volumeLevel = 0

    # Scroll buffer
    LineBuffer = []
    BufferIndex = []

    def __init__(self):
        self.epd = epd2in9.EPD()
        logging.info("init and Clear")
        # Create line frame
        # 255: clear the frame
        self.frame = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.frame)
        self.clear()

        self.font = ImageFont.truetype(fontType, self.font_size)
        # Create scroll line buffers
        for i in range(0, self.total_lines):
            self.LineBuffer.append('')
            self.BufferIndex.append(0)

        self.oversize = self.WRAP

    def clear(self):
        self.frame = Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw = ImageDraw.Draw(self.frame)
        self.epd.init(self.epd.lut_full_update)
        self.epd.Clear(0xFF)

    def draw(self, buffer=[]):
        i = 0
        for line in buffer:
            self.draw.text((10, 0), line, font=font24, fill=0)
            i += 1

        self.epd.display(self.epd.getbuffer(self.draw))
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
    def _out(self, line_number, text=""):
        self.LineBuffer[line_number-1] = text
        return

    def _wrap(self, line_number, text=""):
        self.LineBuffer[line_number-1] = text[:self.total_chars]
        self.LineBuffer[line_number] = text[self.total_chars:]
        return

    # Set oversize text behaviour
    def setWrap(self, mode):
        if mode >= self.TRUNCATE and mode <= self.WRAP:
            self.oversize = mode

    # Update the display
    def update(self):
        # Write text to lines
        for i in range(0, self.total_lines):
            text = self.LineBuffer[i]
            print(i+1, text)
            if len(text) > 0 or self.BufferIndex[i] > 0:
                line_number = i+1
                image_width, image_height = self.frame.size
                print(image_width, image_height)
                # self.draw.rectangle((0, 0, image_width, image_height),
                #                    fill=self.line_fill)

                self.draw.text((10, (line_number - 1) * 20), text, font=self.font,
                               fill=self.char_fill)
                """"
                xPos = 0
                yPos = (line_number - 1) * image_height

                xPos = self.height - image_width - xPos
                self.epd.set_frame_memory(self.frame.transpose(Image.ROTATE_90),
                                          yPos, xPos)
                """

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

    def display_info(self, song_metadata):
        track = ""
        album = ""
        composer = ""
        classical = False

        pass


"""
try:
    logging.info("epd2in9 Demo")

    epd = epd2in9.EPD()
    logging.info("init and Clear")
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width),
                       255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((10, 0), 'hello world', font=font24, fill=0)
    draw.text((10, 20), '2.9inch e-Paper', font=font24, fill=0)
    draw.text((150, 0), u'微雪电子', font=font24, fill=0)
    draw.line((20, 50, 70, 100), fill=0)
    draw.line((70, 50, 20, 100), fill=0)
    draw.rectangle((20, 50, 70, 100), outline=0)
    draw.line((165, 50, 165, 100), fill=0)
    draw.line((140, 75, 190, 75), fill=0)
    draw.arc((140, 50, 190, 100), 0, 360, fill=0)
    draw.rectangle((80, 50, 130, 100), fill=0)
    draw.chord((200, 50, 250, 100), 0, 360, fill=0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    # Drawing on the Vertical image
    logging.info("2.Drawing on the Vertical image...")
    Limage = Image.new('1', (epd.width, epd.height),
                       255)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    draw.text((2, 0), 'hello world', font=font18, fill=0)
    draw.text((2, 20), '2.9inch epd', font=font18, fill=0)
    draw.text((20, 50), u'微雪电子', font=font18, fill=0)
    draw.line((10, 90, 60, 140), fill=0)
    draw.line((60, 90, 10, 140), fill=0)
    draw.rectangle((10, 90, 60, 140), outline=0)
    draw.line((95, 90, 95, 140), fill=0)
    draw.line((70, 115, 120, 115), fill=0)
    draw.arc((70, 90, 120, 140), 0, 360, fill=0)
    draw.rectangle((10, 150, 60, 200), fill=0)
    draw.chord((70, 150, 120, 200), 0, 360, fill=0)
    epd.display(epd.getbuffer(Limage))
    time.sleep(2)

    logging.info("3.read bmp file")
    Himage = Image.open(os.path.join(picdir, '2in9.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    logging.info("4.read bmp file on window")
    Himage2 = Image.new('1', (epd.height, epd.width),
                        255)  # 255: clear the frame
    bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    Himage2.paste(bmp, (50, 10))
    epd.display(epd.getbuffer(Himage2))
    time.sleep(2)

    # partial update
    logging.info("5.show time")
    epd.init(epd.lut_partial_update)
    epd.Clear(0xFF)
    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    num = 0
    while (True):
        time_draw.rectangle((10, 10, 120, 50), fill=255)
        time_draw.text((10, 10), time.strftime(
            '%H:%M:%S'), font=font24, fill=0)
        newimage = time_image.crop([10, 10, 120, 50])
        time_image.paste(newimage, (10, 10))
        epd.display(epd.getbuffer(time_image))

        num = num + 1
        if(num == 10):
            break

    logging.info("Clear...")
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in9.epdconfig.module_exit()
    exit()
"""

if __name__ == "__main__":
    logging.info("start")
    import time
    import datetime
    epd = EpdDisplay()
    epd.setWrap(epd.WRAP)
    epd.reverse(False)
    epd.clear()
    volume = 90
    try:
        while True:
            text = time.strftime('%d/%m/%Y %H:%M')
            epd.out(1, text)
            epd.out(2, "Bob Rathbone")
            epd.out(3, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            #epd.out(4, "0123456789 0123456789 0123456789 0123456789 0123456789 ")
            # pdb.set_trace()
            # epd.out(4,"0123456789",no_interrupt)

            epd.update()
            volume -= 5
            if volume < 0:
                volume = 90
            break

    except KeyboardInterrupt:
        print("\nExit")
        epd.sleep()
        sys.exit(0)
