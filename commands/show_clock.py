#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'img')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'fonts')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in9
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

def start_centered_text(text_len, font_size):
    return round((296 - (text_len * font_size)) / 2)


# 296*128

try:
    logging.info("epd2in9 Demo")
    
    epd = epd2in9.EPD()
    logging.info("init")
    epd.init(epd.lut_full_update)
    logging.info("Clear")
    epd.Clear(0xFF)
    logging.info("Start sleeping")
    time.sleep(2)

    logging.info("Loading fonts")
    font48 = ImageFont.truetype(os.path.join(fontdir, 'Anonymous.ttf'), 48)
    font36 = ImageFont.truetype(os.path.join(fontdir, 'Anonymous.ttf'), 36)
    font24 = ImageFont.truetype(os.path.join(fontdir, 'Anonymous.ttf'), 24)
    font18 = ImageFont.truetype(os.path.join(fontdir, 'Anonymous.ttf'), 18)
    logging.info("End loading fonts")
    
  
    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
#    time_draw.rectangle((35, 35, 130, 80), fill = 255)
    time_draw.line((1, 1, 1, 129), fill = 0)
    text = time.strftime('%A, %d %b')
    text_len = len(text)
    start = start_centered_text(text_len, 24)
    logging.info("start=" + str(start))
    logging.info("text_len=" + str(text_len))
    time_draw.text((start if start > 0 else 10, 10), text, font = font24, fill = 0)
    time_draw.text((65, 40), time.strftime('%H:%M'), font = font48, fill = 0)
    epd.display(epd.getbuffer(time_image))
    
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)
    time.sleep(2)
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in9.epdconfig.module_exit()
    exit()


