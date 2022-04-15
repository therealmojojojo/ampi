# https://www.circuitbasics.com/using-potentiometers-with-raspberry-pi/

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

pin_a = 6
pin_b = 16

def discharge():
    GPIO.setup(pin_a, GPIO.IN)
    GPIO.setup(pin_b, GPIO.OUT)
    GPIO.output(pin_b, False)
    time.sleep(0.004)

def charge_time():
    GPIO.setup(pin_b, GPIO.IN)
    GPIO.setup(pin_a, GPIO.OUT)
    count = 0
    GPIO.output(pin_a, True)
    while not GPIO.input(pin_b):
        count = count + 1
    return count

def analog_read():
    discharge()
    return charge_time()

while True:
    print(analog_read())              
    time.sleep(1)