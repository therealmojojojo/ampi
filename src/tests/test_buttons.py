from gpiozero import Button 
import time
from signal import pause
import sys

# import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
# GPIO.setwarnings(False) # Ignore warning for now
# GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)


def play_handler():
    print("Play pressed")

def stop_handler():
    print("Stop pressed")

# while True: # Run forever
#     if GPIO.input(36) == GPIO.HIGH:
#         print("Button was pushed!")

play = Button(6)
stop = Button(16)

stop.when_pressed = stop_handler

pause()
