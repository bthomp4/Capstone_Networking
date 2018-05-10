# This program is used for the testing the client side with the PiCamera & Sensors

from socket import *
import argparse

import signal
import sys

# for encoding the image 
import base64
from PIL import Image

from time import *

# for GPIO Pins (can only be tested on RPi)
import RPi.GPIO as GPIO

# ------------------
# Defining Variables
# ------------------

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER_LEFT  = 23
GPIO_ECHO_LEFT     = 24
GPIO_TRIGGER_RIGHT = 5
GPIO_ECHO_RIGHT    = 6

# Speed of sound in in/s at temperature
speedSound = 13500 # in/s

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER_LEFT,GPIO.OUT) # Trigger 1
GPIO.setup(GPIO_ECHO_LEFT,GPIO.IN)     # Echo 1
GPIO.setup(GPIO_TRIGGER_RIGHT,GPIO.OUT) # Trigger 2
GPIO.setup(GPIO_ECHO_RIGHT,GPIO.IN)     # ECHO 2

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER_LEFT, False)
GPIO.output(GPIO_TRIGGER_RIGHT, False)

# Set file names
picture = "test.jpg"

# Set variables
DATA_SIZE   = 500
MSS_1       = "0001"
SN_1        = "0001"
VOID_DATA   = "VOID"
SS_FlagSize = 4
SN_FlagSize = 4
DCNT_flag   = 0
takeMeasurement_sleep = 0.00001
settleModule_sleep = 0.5
betweenMeasurements_sleep = 0.05

# -------------------
# Defining Functions
# -------------------

def TakeMeasurement(Trigger, Echo):
    GPIO.output(Trigger,True)
    # Wait 10us
    sleep(takeMeasurement_sleep)
    GPIO.output(Trigger,False)
    start = time()

    while GPIO.input(Echo)==0:
        start = time()

    while GPIO.input(Echo)==1:
        stop = time()

    stop = time()

    elapsed = stop-start
    distance = (elapsed * speedSound/2)

    return distance

# ------------------------------------------------------------------
# UpdateSideSensors updates the sensor values and returns the values
# ------------------------------------------------------------------
def UpdateSideSensors():

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER_LEFT,False)
    GPIO.output(GPIO_TRIGGER_RIGHT,False)

    n = 3
    numPingRight = 0
    numPingLeft = 0
    flagRight = "N"
    flagLeft = "N"

    for i in range( 0,n ):
        leftMeasure = TakeMeasurement(GPIO_TRIGGER_LEFT, GPIO_ECHO_LEFT)
        sleep(betweenMeasurements_sleep)
        if (leftMeasure < 120):
            print(str(i) + "Left Measure" + str(leftMeasure))
            numPingLeft = numPingLeft + 1
        rightMeasure = TakeMeasurement(GPIO_TRIGGER_RIGHT, GPIO_ECHO_RIGHT)
        sleep(betweenMeasurements_sleep)
        if (rightMeasure < 120):
            print(str(i) + "Right Measure" + str(rightMeasure))
            numPingRight = numPingRight + 1
    if ( numPingLeft > (n/2) ):
        flagLeft = "Y"
    if ( numPingRight > (n/2) ):
        flagRight = "Y"

    return flagLeft, flagRight

# --------------------------------------------
# splitData is used to split data based on '!'
# --------------------------------------------
def splitData(data):
    data_decoded = data.decode()
    newData = data_decoded.split('!')
    data1 = newData[0]
    data2 = newData[1]

    return data1, data2

# ---------------
# Main Script
# ---------------

sleep(settleModule_sleep)

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

def signal_handler(signal,frame):
    GPIO.cleanup()
    client_socket.close()
    print("full: " + str(sum(times)/len(times)))
    #print("loop: " + str(sum(loop)/len(loop)))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

start = 0
stop = 0
times = []
flag = False
lstart = 0
lstop = 0
loop = []
while True:

    print("start process")
    start = time()
            
    print("Handling Sensor Data")
    # Send DATA_SEN message
    LS, RS = UpdateSideSensors()

    msg_data = LS + '!' + RS

    message = msg_data
    client_socket.sendto(message.encode(), (args.server_name,server_port))

    # Send DATA_SYN
    print("Sending Data_SYN")
    message = "SEN!VOID"
    client_socket.sendto(message.encode(), (args.server_name,server_port))

    # Wait for DATA_ACK from Server
    print("Receiving DATA_ACK")
    response,serverAddress = client_socket.recvfrom(2048)

    # Then send a FULL_DATA_SYN
    msg_data = "ben is mean"
    print("Sending FULL_DATA_SYN")
    message = msg_data
    client_socket.sendto(message.encode(), (args.server_name,server_port))

    stop = time()
    print("end process")
    times.append(stop - start)
