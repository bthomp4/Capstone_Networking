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

from picamera import PiCamera

# ------------------
# Defining Variables
# ------------------

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER1 = 23
GPIO_ECHO1    = 24
GPIO_TRIGGER2 = 5
GPIO_ECHO2    = 6

# Speed of sound in in/s at temperature
speedSound = 13500 # in/s

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER1,GPIO.OUT) # Trigger 1
GPIO.setup(GPIO_ECHO1,GPIO.IN)     # Echo 1
GPIO.setup(GPIO_TRIGGER2,GPIO.OUT) # Trigger 2
GPIO.setup(GPIO_ECHO2,GPIO.IN)     # ECHO 2

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER1, False)
GPIO.output(GPIO_TRIGGER2, False)

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

# Dictionaries for Flag Values
dictRec = {'0':'INIT_SYN','1':'INIT_SYNACK','2':'INIT_ACK','3':'FULL_DATA_SYN','4':'FULL_DATA_ACK','5':'SYNC_SYN','6':'SYNC_ACK','7':'DATA_SYN','8':'DATA_ACK','9':'DATA_CAM','A':'DATA_SEN','B':'MODE_SYN','C':'MODE_ACK'}

dictSend = {'INIT_SYN':'0','INIT_SYNACK':'1','INIT_ACK':'2','FULL_DATA_SYN':'3','FULL_DATA_ACK':'4','SYNC_SYN':'5','SYNC_ACK':'6','DATA_SYN':'7','DATA_ACK':'8','DATA_CAM':'9','DATA_SEN':'A','MODE_SYN':'B','MODE_ACK':'C'}

# for the mode of the system, FB or BS
sys_mode = " "

# -------------------
# Defining Functions
# -------------------

# --------------------------------------------------
# MeasureLeft takes a measurement from the left sensor
# --------------------------------------------------
def MeasureLeft():
    # This function measures a distance
    GPIO.output(GPIO_TRIGGER1,True)
    # Wait 10us
    sleep(0.00001)
    GPIO.output(GPIO_TRIGGER1,False)
    start = time()

    while GPIO.input(GPIO_ECHO1)==0:
        start = time()

    while GPIO.input(GPIO_ECHO1)==1:
        stop = time()

    stop = time()

    elapsed = stop-start
    distance = (elapsed * speedSound/2)

    return distance

# ---------------------------------------------------
# MeasureRight takes a measurement from the right sensor
# ---------------------------------------------------
def MeasureRight():
    # This function measures a distance
    GPIO.output(GPIO_TRIGGER2,True)
    # Wait 10us
    sleep(0.00001)
    GPIO.output(GPIO_TRIGGER2,False)
    start = time()

    while GPIO.input(GPIO_ECHO2)==0:
        start = time()

    while GPIO.input(GPIO_ECHO2)==1:
        stop = time()

    stop = time()

    elapsed = stop-start
    distance = (elapsed * speedSound)/2

    return distance

# ------------------------------------------------------------------
# UpdateSideSensors updates the sensor values and returns the values
# ------------------------------------------------------------------
def UpdateSideSensors():

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER1,False)
    GPIO.output(GPIO_TRIGGER2,False)

    n = 3
    numPingRight = 0
    numPingLeft = 0
    flagRight = "N"
    flagLeft = "N"

    for i in range( 0,n ):
        leftMeasure = MeasureLeft()
        if (leftMeasure < 120):
            print(str(i) + "Left Measure" + str(leftMeasure))
            numPingLeft = numPingLeft + 1
        rightMeasure = MeasureRight()
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

sleep(0.5)

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

def signal_handler(signal,frame):
    GPIO.cleanup()
    client_socket.close()
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
    msg_data = sys_mode + '!' + "SEN"
    print("Sending FULL_DATA_SYN")
    message = msg_data
    client_socket.sendto(message.encode(), (args.server_name,server_port))

client_socket.close()
