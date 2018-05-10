import RPi.GPIO as GPIO
from time import *


LEDs = 0


# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
pin = 21
# Set pins as output and input
GPIO.setup(pin,GPIO.OUT) 

# Set trigger to False (Low)
GPIO.output(pin, False)

sleep(0.5)

def status1():
    print("Status 1")
    count = 0
    while count < 20:
        GPIO.output(pin, False)
        sleep(.1)
        GPIO.output(pin, True)
        sleep(.1)
        count = count + 1

def status4():
    print("Status 4")
    count = 0
    while count < 200:
        GPIO.output(pin, False)
        sleep(.01)
        GPIO.output(pin, True)
        sleep(.01)
        count = count + 1
def status2():
    print("Status 2")
    count = 0
    while count < 20:
        GPIO.output(pin, False)
        sleep(.15)
        GPIO.output(pin, True)
        sleep(.05)
        count = count + 1
def status3():
    print("Status 3")
    count = 0
    while count < 20:
        GPIO.output(pin, True)
        sleep(.15)
        GPIO.output(pin, False)
        sleep(.05)
        count = count + 1
def status5():
    print("Status 5")
    count = 0
    while count < 20:
        GPIO.output(pin, True)
        sleep(.1)
        GPIO.setup(pin, GPIO.IN)
        sleep(.1)
        GPIO.setup(pin, GPIO.OUT)
        count = count +1

def status6():
    print("Status 6")
    count = 0
    while count < 20:
        GPIO.output(pin, False)
        sleep(.1)
        GPIO.setup(pin, GPIO.IN)
        sleep(.1)
        GPIO.setup(pin, GPIO.OUT)
        count = count +1
# --------- main ------


try:
    status1()
    status2()
    status3()
    status4()
    status5()
    status6()
except KeyboardInterrupt:
    pass
GPIO.cleanup()
