import RPi.GPIO as GPIO

from time import *


LEDs = 0

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
    global LEDs
    # Number of Measurements being taken
    n = 3

    # Initialized to zero
    
    lightLeds = []
    listDist = []
    for i in range(0,n):
        listDist.append(MeasureLidar())

    #listDist.sort()

    #avgDist = listDist[0]
    
    print(listDist)

    last = listDist.pop()
    for d in listDist:
    
        if d < 12 and last < 12:
            LEDs = 8
            break
        elif d >= 12 and d < 24 and last >= 12 and last < 24:
            LEDs = 7
            break
        elif d >= 24 and d < 36 and last >= 24 and last < 36:
            LEDs = 6
            break
        elif d >= 36 and d < 48 and last >= 36 and last < 48:
            LEDs = 5
            break
        elif d >= 48 and d < 60 and last >= 48 and last < 60:
            LEDs = 4
            break
        elif d >= 60 and d < 72 and last >= 60 and last < 72:
            LEDs = 3
            break
        elif d >= 72 and d < 80 and last >= 72 and last < 80:
            LEDs = 2
            break
        elif d >= 80 and d < 100 and last >= 80 and last < 100:
            LEDs = 1
            break

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

try:

    while True:
        UpdateLidar()
        sleep(0.5) # take this out later
        print("Number of Leds Lighting up:" + str(LEDs))     

except KeyboardInterrupt:
    GPIO.cleanup()
