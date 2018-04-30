import RPi.GPIO as GPIO

from time import *

# ------------------------------------------------
# MeasureLidar takes measurement to nearest object
# in front of the rider. Returns the distance to
# that object
# ------------------------------------------------

def MeasureLidar():
    # This function measures a distance
    GPIO.output(GPIO_lidarTrigger, True)
    # Wait 10us
    sleep(0.00001) # this is needed
    GPIO.output(GPIO_lidarTrigger, False)
    start = time()

    while GPIO.input(GPIO_lidarEcho) == 0:
        start = time()

    while GPIO.input(GPIO_lidarEcho) == 1:
        stop = time()

    stop = time()

    elapsed = stop - start # every 10 microseconds = 1 cm
    distance = elapsed * (10  ** 5) # in cm
    distance = distance  * 0.0328084 # in feet

    return distance

# This function takes 'n' measurements and
# returns how many LEDs should be on
def UpdateLidar():

    n = 3
    numLEDs = 0

    sumDist = 0
    for i in range( 0,n ):
        sumist = sumDist + MeasureLidar()
    avgDist = sumDist / n

    listDist = []
    for i in range(n):
        listDist.append(MeasureLidar())
    listDist.sort()

    avgDist = listDist[0]   #not true, lazy programming
    if avgDist >= 12 and avgDist < 24:
        numLEDs = 1
    elif avgDist >= 24 and avgDist < 36:
        numLEDs = 2
    elif avgDist >= 36 and avgDist < 48:
        numLEDs = 3
    elif avgDist >= 48 and avgDist < 60:
        numLEDs = 4
    elif avgDist >= 60 and avgDist < 72:
        numLEDs = 5
    elif avgDist >= 72 and avgDist < 84:
        numLEDs = 6
    elif avgDist >= 84 and avgDist < 96:
        numLEDs = 7
    elif avgDist >= 96 and avgDist < 108:
        numLEDs = 8

    return numLEDs

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_lidarTrigger = 23
GPIO_lidarEcho    = 20

# Set pins as output and input
GPIO.setup(GPIO_lidarTrigger,GPIO.OUT) # Trigger 1
GPIO.setup(GPIO_lidarEcho,GPIO.IN)     # Echo 1

# Set trigger to False (Low)
GPIO.output(GPIO_lidarTrigger, False)

sleep(0.5)

# --------- main ------
numLeds = UpdateLidar()
