#!/usr/bin/env python

import RPi.GPIO as GPIO
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(3, GPIO.FALLING)

notDetected = True

while notDetected:
    print("Power on")

    if GPIO.event_detected(3):
        print("Flash LEDs")
        print("Shutting down...")
        notDetected = False

subprocess.call(['shutdown', '-h', 'now'], shell=False)
