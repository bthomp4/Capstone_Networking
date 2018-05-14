# This is the final version of the server program for the front unit
from socket import *
from errno import *

# for decoding and displaying the image
import base64
from PIL import Image, ImageTk
import tkinter

from time import *

import signal
import sys
import subprocess

import RPi.GPIO as GPIO

# ------------------
# Defining Variables
# ------------------

# Set variables
noConnect = True # Boolean for stating connection of a client
hasLost = False # Boolean for packet loss
frontLEDs = 0
settleSleep = 0.5
measurementSleep = 0.00001
MSS = 9999 # Max Segment Size
picture = "~/Capstone_Networking/test_decode.jpg"
logo = "~/Capstone_Networking/logo.jpg"
encode_string = []
check_pt = 0    # where packets need to be checked for loss
cp_value = 1    # SS/cp_value = num of packets sent per check
packetsRec = [0] * MSS    # stores packets that have been received

# Dictionaries for Flag Values
dictRec = {'0':"INIT_SYN",'1':"INIT_SYNACK",'2':"INIT_ACK",'3':"FULL_DATA_SYN",'4':"FULL_DATA_ACK",'5':"SYNC_SYN",'6':"SYNC_ACK",'7':"DATA_SYN",'8':"DATA_ACK",'9':"DATA_CAM",'A':"DATA_SEN",'B':"MODE_SYN",'C':"MODE_ACK", 'D':"DCNT"}

dictSend = {"INIT_SYN":'0',"INIT_SYNACK":'1',"INIT_ACK":'2',"FULL_DATA_SYN":'3',"FULL_DATA_ACK":'4',"SYNC_SYN":'5',"SYNC_ACK":'6',"DATA_SYN":'7',"DATA_ACK":'8',"DATA_CAM":'9',"DATA_SEN":'A',"MODE_SYN":'B',"MODE_ACK":'C',"DCNT":'D'}

# GPIO pins (BCM) and their purpose
GPIO.setmode(GPIO.BCM)
GPIO_MODE_SEL   = 16
GPIO_TRIGGER    = 23
GPIO_ECHO       = 20
GPIO_LEDS_RIGHT = 21
GPIO_LEDS_LEFT  = 27
GPIO_LED_SEL0   = 2
GPIO_LED_SEL1   = 14
GPIO_LED_SEL2   = 4    #MSB
GPIO_LED_EN     = 17
GPIO_LED_STAT   = 11
GPIO_SAFE_SD    = 3
GPIO_LBO        = 26

# Set pins as output and input
GPIO.setup(GPIO_MODE_SEL,GPIO.IN)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)
GPIO.setup(GPIO_LEDS_RIGHT,GPIO.OUT)
GPIO.setup(GPIO_LEDS_LEFT,GPIO.OUT)
GPIO.setup(GPIO_LED_SEL0,GPIO.OUT)
GPIO.setup(GPIO_LED_SEL1,GPIO.OUT)
GPIO.setup(GPIO_LED_SEL2,GPIO.OUT)
GPIO.setup(GPIO_LED_EN,GPIO.OUT)
GPIO.setup(GPIO_LED_STAT, GPIO.OUT)

GPIO.setup(GPIO_SAFE_SD, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(GPIO_SAFE_SD, GPIO.FALLING)

GPIO.setup(GPIO_LBO, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(GPIO_LBO, GPIO.RISING)

GPIO.output(GPIO_TRIGGER,False)
GPIO.output(GPIO_LEDS_RIGHT, False)
GPIO.output(GPIO_LEDS_LEFT, False)
GPIO.output(GPIO_LED_SEL0, False)
GPIO.output(GPIO_LED_SEL1, False)
GPIO.output(GPIO_LED_SEL2, False)
GPIO.output(GPIO_LED_EN, False)
GPIO.output(GPIO_LED_STAT, False)

# ------------------
# Defining Functions
# ------------------

# -----------------------------------------------
# decode_string decodes the image from the client
# -----------------------------------------------
def decode_string(image_64_encode):
    global encode_string
    encode_string = []
    image_64_decode = base64.decodestring(image_64_encode)
    with open(picture,'wb') as image_result:
        image_result.write(image_64_decode)
    update_image()

# ----------------------------------------------
# update_image: updates the image being displayed
# ----------------------------------------------
def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open(picture))
    label.config(image = camImg)
    label.pack()

# ---------------------------------------------------------------------------
# check_point: sends to client a data_ack indicating if there was packet loss
# ---------------------------------------------------------------------------
def check_point(SegmentSize):
    global check_pt
    global packetsRec

    packet_dropped = -1
    for i in range (check_pt,(check_pt + (SegmentSize//cp_value))):
        if packetsRec[i] == 0:
            packet_dropped = i
            break

    # Sending DATA_ACK
    message = dictSend["DATA_ACK"] + ",0001,0001,CAM!" + str(packet_dropped)

    serverSocket.sendto(message.encode(),clientAddress)

    return packet_dropped

# --------------------------------------------
# splitData is used to split data based on '!'
# --------------------------------------------
def splitData(data):
    data_decoded = data.decode()
    newData = data_decoded.split('!')
    data1 = newData[0]
    data2 = newData[1]

    return data1, data2

# ------------------------------------------------
# MeasureLidar takes measurement to nearest object
# in front of the rider. Returns the distance to
# that object
# ------------------------------------------------
def MeasureLidar():
    # This function measures a distance
    GPIO.output(GPIO_TRIGGER, True)
    # Wait 10us
    sleep(measurementSleep)
    GPIO.output(GPIO_TRIGGER, False)
    start = time()

    while GPIO.input(GPIO_ECHO) == 0:
        start = time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop = time()

    stop = time()

    elapsed = stop - start # every 10 microseconds = 1 cm
    distance = elapsed * (10  ** 5) # in cm
    distance = distance  * 0.0328084 # in feet

    return distance

# -----------------------------------------
# UpdateLidar takes 'n' measurements and
# sets the value for the number of LEDs to
# be turned on.
# -----------------------------------------
def UpdateLidar():
    global frontLEDs

    n = 3 # num of measurements taken

    listDist = []
    for i in range(0,n):
        listDist.append(MeasureLidar())

    last = listDist.pop()
    for d in listDist:

        if d < 12 and last < 12:
            frontLEDs = 8
            break
        elif d >= 12 and d < 24 and last >= 12 and last < 24:
            frontLEDs = 7
            break
        elif d >= 24 and d < 36 and last >= 24 and last < 36:
            frontLEDs = 6
            break
        elif d >= 36 and d < 48 and last >= 36 and last < 48:
            frontLEDs = 5
            break
        elif d >= 48 and d < 60 and last >= 48 and last < 60:
            frontLEDs = 4
            break
        elif d >= 60 and d < 72 and last >= 60 and last < 72:
            frontLEDs = 3
            break
        elif d >= 72 and d < 80 and last >= 72 and last < 80:
            frontLEDs = 2
            break
        elif d >= 80 and d < 100 and last >= 80 and last < 100:
            frontLEDs = 1
            break

# ---------------
# Main Script
# ---------------

# Allow for time for setting up GPIO
sleep(settleSleep)

# Setting up socket
server_port = 12000
serverSocket = socket(AF_INET,SOCK_DGRAM)
serverSocket.bind(('',server_port))

# Setting up gui for displaying image
w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()
w.update()

# Setting the mode of the system
loop_count = 0
color = False
while loop_count < 15:
    color = not color
    sleep(.1)
    loop_count = loop_count + 1

if GPIO.input(GPIO_MODE_SEL):
    sys_mode = "FB"
else:
    sys_mode = "BS"

loop_count = 0
while loop_count < 150:
    if sys_mode == "BS":
        GPIO.output(GPIO_LED_STAT, False)
        sleep(.01)
        GPIO.output(GPIO_LED_STAT, True)
        sleep(.01)
    else:
        GPIO.output(GPIO_LED_STAT, True)
        sleep(.02)
    loop_count = loop_count + 1

loop_count = 0
color = False
serverSocket.setblocking(False) # to allow for the loop to process
# Initial Handshaking loop
while noConnect:
    sleep(0.1)
    color = not color
    GPIO.output(GPIO_LED_STAT, color)
    try:
        message_rec = True
        response, clientAddress = serverSocket.recvfrom(2048)
    except error as e:
        if e.errno is 107 or e.errno is 11:
            message_rec = False
    if message_rec:

        splitPacket = response.split(b',')

        if dictRec[splitPacket[0].decode()] == "INIT_SYN":
            # send back INIT_SYNACK
            message = dictSend["INIT_SYNACK"] + ",0001,0001,VOID"

            serverSocket.sendto(message.encode(),clientAddress)
        elif dictRec[splitPacket[0].decode()] == "INIT_ACK":
            # Send back MODE_SYN
            message = dictSend["MODE_SYN"] + ",0001,0001," + sys_mode
            serverSocket.sendto(message.encode(),clientAddress)

            noConnect = False
            message = "Connected"
            serverSocket.setblocking(True)
            # Wait for MODE_ACK, DATA = "MODE"
            response, clientAddress = serverSocket.recvfrom(2048)

            # send back FULL_DATA_ACK, DATA = "MODE!VOID"
            message = dictSend["FULL_DATA_ACK"] + ",0001,0001," + sys_mode + "!VOID"
            serverSocket.sendto(message.encode(),clientAddress)

        elif dictRec[splitPacket[0].decode()] == "DCNT":
            disconnect()

GPIO.setup(GPIO_LED_STAT, GPIO.IN)
led_flag = False

# begin loop
while True:
   if led_flag:
        GPIO.setup(GPIO_LED_STAT, GPIO.OUT)
        GPIO.output(GPIO_LED_STAT, True)
    else:
        GPIO.setup(GPIO_LED_STAT, GPIO.IN)
    response, clientAddress = serverSocket.recvfrom(2048)
    splitPacket = response.split(b',')
    print(dictRec[splitPacket[0].decode()])

    if GPIO.event_detected(GPIO_SAFE_SD) or GPIO.event_detected(GPIO_LBO):
        message = dictSend["DCNT"] + ",0001,0001,VOID"
        serverSocket.sendto(message.encode(),clientAddress)
        disconnect()

    if dictRec[splitPacket[0].decode()] == "FULL_DATA_SYN":

        sys_mode,data_type = splitData(splitPacket[3])

        if data_type == "CAM":
            led_flag = not led_flag
            #reset values
            check_pt = 0
            packetsRec = [0] * MSS

            full_string = b''
            i = 0

            while(i < len(encode_string)):
                full_string = full_string + encode_string[i]
                i = i + 1

            decode_string(full_string)

            message = dictSend["FULL_DATA_ACK"] + ",0001,0001," + sys_mode + "!CAM"
            serverSocket.sendto(message.encode(),clientAddress)
        elif data_type == "SEN":
            message = dictSend["FULL_DATA_ACK"] + ",0001,0001," + sys_mode + "!SEN"
            serverSocket.sendto(message.encode(),clientAddress)

    elif dictRec[splitPacket[0].decode()] == "SYNC_SYN":

        data_type,SS = splitData(splitPacket[3])
        SegmentSize = int(SS)

        message = dictSend["SYNC_ACK"] + ",0001,0001," + data_type + '!' + SS
        serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == "DATA_SYN":

        data_type,other_data = splitData(splitPacket[3])

        if data_type == "CAM":
            #check for packet loss

            SegmentSize = int(other_data)

            packet_dropped = check_point(SegmentSize)

            if (packet_dropped == -1):
                hasLost = False
                check_pt = check_pt + (SegmentSize//cp_value)
            else:
                hasLost = True
        elif data_type == "SEN":
            message = dictSend["DATA_ACK"] + ",0001,0001,SEN!VOID"
            serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == "DATA_CAM":

        SegmentSize = int(splitPacket[1])
        SegmentNum = int(splitPacket[2])

        packetsRec[SegmentNum] = 1

        # Append the encoded image data
        if (SegmentNum == len(encode_string) or hasLost == False):
            encode_string.append(splitPacket[3])
        else:
            encode_string[SegmentNum] = splitPacket[3]

    elif dictRec[splitPacket[0].decode()] == "DATA_SEN":
        # handle the sensor data
        LS,RS = splitData(splitPacket[3])

        UpdateLidar()

        if frontLEDs == 0:
            GPIO.output(GPIO_LED_SEL0, False)
            GPIO.output(GPIO_LED_SEL1, False)
            GPIO.output(GPIO_LED_SEL2, False)
            GPIO.output(GPIO_LED_EN, False)
        elif frontLEDs == 1:
            GPIO.output(GPIO_LED_SEL0, False)
            GPIO.output(GPIO_LED_SEL1, False)
            GPIO.output(GPIO_LED_SEL2, False)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 2:
            GPIO.output(GPIO_LED_SEL0, True)
            GPIO.output(GPIO_LED_SEL1, False)
            GPIO.output(GPIO_LED_SEL2, False)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 3:
            GPIO.output(GPIO_LED_SEL0, False)
            GPIO.output(GPIO_LED_SEL1, True)
            GPIO.output(GPIO_LED_SEL2, False)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 4:
            GPIO.output(GPIO_LED_SEL0, True)
            GPIO.output(GPIO_LED_SEL1, True)
            GPIO.output(GPIO_LED_SEL2, False)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 5:
            GPIO.output(GPIO_LED_SEL0, False)
            GPIO.output(GPIO_LED_SEL1, False)
            GPIO.output(GPIO_LED_SEL2, True)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 6:
            GPIO.output(GPIO_LED_SEL0, True)
            GPIO.output(GPIO_LED_SEL1, False)
            GPIO.output(GPIO_LED_SEL2, True)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 7:
            GPIO.output(GPIO_LED_SEL0, False)
            GPIO.output(GPIO_LED_SEL1, True)
            GPIO.output(GPIO_LED_SEL2, True)
            GPIO.output(GPIO_LED_EN, True)
        elif frontLEDs == 8:
            GPIO.output(GPIO_LED_SEL0, True)
            GPIO.output(GPIO_LED_SEL1, True)
            GPIO.output(GPIO_LED_SEL2, True)
            GPIO.output(GPIO_LED_EN, True)

        if RS == "Y":
            GPIO.output(GPIO_LEDS_RIGHT,True)
        else:
            GPIO.output(GPIO_LEDS_RIGHT,False)
        if LS == "Y":
            GPIO.output(GPIO_LEDS_LEFT,True)
        else:
            GPIO.output(GPIO_LEDS_LEFT,False)

    elif dictRec[splitPacket[0].decode()] == "DCNT":
        # Handle Disconnect from Client
        print("Handle DCNT")
        disconnect()

    w.update()
    w.update_idletasks()
