from socket import *

# for decoding and displaying the image
import base64
from PIL import Image,ImageTk
import tkinter

from time import *

import signal
import sys

import RPi.GPIO as GPIO

# ------------------
# Defining Variables
# ------------------

# Set variables
HasLost = False
VOID_DATA = "VOID"

picture = "test_decode.jpg"
logo = "logo.jpg"

# array to hold encoded string from client
encode_string = []

# Max Segment Size
MSS   = 9999
MSS_1 = "0001"
SN_1  = "0001"

# where packets need to be checked for loss
check_pt = 0

# List for storing which packets have been received
packetsRec = [0] * MSS

# Dictionaries for Flag Values
dictRec = {'0':'INIT_SYN','1':'INIT_SYNACK','2':'INIT_ACK','3':'FULL_DATA_SYN','4':'FULL_DATA_ACK','5':'SYNC_SYN','6':'SYNC_ACK','7':'DATA_SYN','8':'DATA_ACK','9':'DATA_CAM','A':'DATA_SEN','B':'MODE_SYN','C':'MODE_ACK'}

dictSend = {'INIT_SYN':'0','INIT_SYNACK':'1','INIT_ACK':'2','FULL_DATA_SYN':'3','FULL_DATA_ACK':'4','SYNC_SYN':'5','SYNC_ACK':'6','DATA_SYN':'7','DATA_ACK':'8','DATA_CAM':'9','DATA_SEN':'A','MODE_SYN':'B','MODE_ACK':'C'}

# GPIO pins (BCM) and their purpose
GPIO.setmode(GPIO.BCM)

#GPIO_ModeSel    = 16

GPIO_lidarTrigger = 23
GPIO_lidarEcho    = 20
GPIO_LEDSRIGHT    = 21
GPIO_LEDSLEFT     = 27

GPIO_FRONTLEDSel0  = 2
GPIO_FRONTLEDSel1  = 14
GPIO_FRONTLEDSel2  = 4    #MSB
GPIO_FRONTLEDEn    = 17
#GPIO_FRONTStatus  = 11

# Set pins as output and input
#GPIO.setup(GPIO_ModeSel,GPIO.IN)

GPIO.setup(GPIO_lidarTrigger,GPIO.OUT) # Trigger 1
GPIO.setup(GPIO_lidarEcho,GPIO.IN)     # Echo 1
GPIO.setup(GPIO_LEDSRIGHT,GPIO.OUT)
GPIO.setup(GPIO_LEDSLEFT,GPIO.OUT)
GPIO.setup(GPIO_FRONTLEDSel0,GPIO.OUT)
GPIO.setup(GPIO_FRONTLEDSel1,GPIO.OUT)
GPIO.setup(GPIO_FRONTLEDSel2,GPIO.OUT)
GPIO.setup(GPIO_FRONTLEDEn,GPIO.OUT)

# Set default values to False (low)
GPIO.output(GPIO_lidarTrigger,False)
GPIO.output(GPIO_LEDSRIGHT, False)
GPIO.output(GPIO_LEDSLEFT, False)
GPIO.output(GPIO_FRONTLEDSel0, False)
GPIO.output(GPIO_FRONTLEDSel1, False)
GPIO.output(GPIO_FRONTLEDSel2, False)
GPIO.output(GPIO_FRONTLEDEn, False)

FrontLEDs = 0

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

    print("Check_Pt: " + str(check_pt))
    packet_dropped = -1
    for i in range (check_pt,(check_pt + (SegmentSize//8))):
        if packetsRec[i] == 0:
            packet_dropped = i
            break
    data = "CAM" + '!' + str(packet_dropped)

    # Sending DATA_ACK
    message = dictSend['DATA_ACK'] + ',' + str(MSS_1) + ',' + str(SN_1) + ',' + data

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
    global FrontLEDs

    # Number of Measurements being taken
    n = 3

    # Initialized to zero

    lightLeds = []
    listDist = []
    for i in range(0,n):
        listDist.append(MeasureLidar())

    print(listDist)

    last = listDist.pop()
    for d in listDist:

        if d < 12 and last < 12:
            FrontLEDs = 8
            break
        elif d >= 12 and d < 24 and last >= 12 and last < 24:
            FrontLEDs = 7
            break
        elif d >= 24 and d < 36 and last >= 24 and last < 36:
            FrontLEDs = 6
            break
        elif d >= 36 and d < 48 and last >= 36 and last < 48:
            FrontLEDs = 5
            break
        elif d >= 48 and d < 60 and last >= 48 and last < 60:
            FrontLEDs = 4
            break
        elif d >= 60 and d < 72 and last >= 60 and last < 72:
            FrontLEDs = 3
            break
        elif d >= 72 and d < 80 and last >= 72 and last < 80:
            FrontLEDs = 2
            break
        elif d >= 80 and d < 100 and last >= 80 and last < 100:
            FrontLEDs = 1
            break
    return FrontLEDs

# ---------------
# Main Script
# ---------------

sleep(0.5)

# Setting up socket
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

def signal_handler(signal,frame):
    GPIO.cleanup()
    serverSocket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Setting up gui for displaying image
w = tkinter.Tk()
im = Image.open(logo)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()
w.update()

# Setting the mode of the system
sys_mode = "FB"

#if GPIO.input(GPIO_ModeSel):
#    sys_mode = "FB"
#else:
#    sys_mode = "BS"

# begin loop
while True:

    # for testing dropped packets
    response, clientAddress = serverSocket.recvfrom(2048)
    splitPacket = response.split(b',')

    if dictRec[splitPacket[0].decode()] == 'INIT_SYN':
        # send back INIT_SYNACK
        print("Received INIT_SYN, sending INIT_SYNACK")
        message = dictSend['INIT_SYNACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + VOID_DATA
        
        serverSocket.sendto(message.encode(),clientAddress) 
    elif dictRec[splitPacket[0].decode()] == 'INIT_ACK':
        # Send back MODE_SYN
        print("Received INIT_ACK, sending MODE_SYN")
        message = dictSend['MODE_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + sys_mode
        serverSocket.sendto(message.encode(),clientAddress)        

        # Wait for MODE_ACK, DATA = "MODE"
        response, clientAddress = serverSocket.recvfrom(2048)

        # send back FULL_DATA_ACK, DATA = "MODE!VOID"
        msg_data = sys_mode + '!' + VOID_DATA
        message = dictSend['FULL_DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + msg_data 

        serverSocket.sendto(message.encode(),clientAddress) 
    elif dictRec[splitPacket[0].decode()] == 'FULL_DATA_SYN':
        print("Received FULL_DATA_SYN")
        
        sys_mode,data_type = splitData(splitPacket[3])

        if data_type == "CAM":

            print("Received Full Picture")
            
            #reset values 
            check_pt = 0
            packetsRec = [0] * MSS        

            full_string = b''
            i = 0

            while(i < len(encode_string)):
                full_string = full_string + encode_string[i]
                i = i + 1
        
            decode_string(full_string)

            msg_data = sys_mode + '!' + "CAM"

            message = dictSend['FULL_DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + msg_data
            serverSocket.sendto(message.encode(),clientAddress)
        elif data_type == "SEN":
            msg_data = sys_mode + '!' + "SEN"

            message = dictSend['FULL_DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + msg_data
            serverSocket.sendto(message.encode(),clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'SYNC_SYN':
        print("Received SYNC_SYN")
                
        data_type,SS = splitData(splitPacket[3])
        SegmentSize = int(SS)

        msg_data = data_type + '!' + SS

        message = dictSend['SYNC_ACK'] + "," + MSS_1 + ',' + SN_1 + ',' + msg_data
        serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'DATA_SYN':
        print("Received DATA_SYN")
        
        data_type,other_data = splitData(splitPacket[3])

        if data_type == "CAM": 
            #check for packet loss

            SegmentSize = int(other_data)

            packet_dropped = check_point(SegmentSize)
       
            if (packet_dropped == -1):
                HasLost = False
                check_pt = check_pt + (SegmentSize//8) 
            else:
                HasLost = True
        elif data_type == "SEN":
            message = dictSend['DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + "SEN!VOID"
            serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'DATA_CAM':
        print("Received DATA_CAM")

        # Second element = SS
        SegmentSize = int(splitPacket[1])

        # Third element = SN
        SegmentNum = int(splitPacket[2]) 
       
        packetsRec[SegmentNum] = 1

        # Append the encoded image data 
        if (SegmentNum == len(encode_string) or HasLost == False):
            encode_string.append(splitPacket[3])
        else:
            encode_string[SegmentNum] = splitPacket[3]

    elif dictRec[splitPacket[0].decode()] == 'DATA_SEN':
        # handle the sensor data

        print("Recieving Sensor Data")
    
        LS,RS = splitData(splitPacket[3])

        numLEDs = UpdateLidar()
        
        if numLEDs == 0:
            GPIO.output(GPIO_FRONTLEDSel0, False)
            GPIO.output(GPIO_FRONTLEDSel1, False)
            GPIO.output(GPIO_FRONTLEDSel2, False)
            GPIO.output(GPIO_FRONTLEDEn, False)
        elif numLEDs == 1:
            GPIO.output(GPIO_FRONTLEDSel0, False)
            GPIO.output(GPIO_FRONTLEDSel1, False)
            GPIO.output(GPIO_FRONTLEDSel2, False)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 2:
            GPIO.output(GPIO_FRONTLEDSel0, True)
            GPIO.output(GPIO_FRONTLEDSel1, False)
            GPIO.output(GPIO_FRONTLEDSel2, False)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 3:
            GPIO.output(GPIO_FRONTLEDSel0, False)
            GPIO.output(GPIO_FRONTLEDSel1, True)
            GPIO.output(GPIO_FRONTLEDSel2, False)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 4:
            GPIO.output(GPIO_FRONTLEDSel0, True)
            GPIO.output(GPIO_FRONTLEDSel1, True)
            GPIO.output(GPIO_FRONTLEDSel2, False)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 5:
            GPIO.output(GPIO_FRONTLEDSel0, False)
            GPIO.output(GPIO_FRONTLEDSel1, False)
            GPIO.output(GPIO_FRONTLEDSel2, True)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 6:
            GPIO.output(GPIO_FRONTLEDSel0, True)
            GPIO.output(GPIO_FRONTLEDSel1, False)
            GPIO.output(GPIO_FRONTLEDSel2, True)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 7:
            GPIO.output(GPIO_FRONTLEDSel0, False)
            GPIO.output(GPIO_FRONTLEDSel1, True)
            GPIO.output(GPIO_FRONTLEDSel2, True)
            GPIO.output(GPIO_FRONTLEDEn, True)
        elif numLEDs == 8:
            GPIO.output(GPIO_FRONTLEDSel0, True)
            GPIO.output(GPIO_FRONTLEDSel1, True)
            GPIO.output(GPIO_FRONTLEDSel2, True)
            GPIO.output(GPIO_FRONTLEDEn, True)

        # Lighting up LEDs for Side Sensors
        if RS == "Y": 
            GPIO.output(GPIO_LEDSRIGHT,True)
            print("Turn Right LEDS ON")
        else:
            GPIO.output(GPIO_LEDSRIGHT,False)
            print("Turn Right LEDS OFF")
        if LS == "Y":
            GPIO.output(GPIO_LEDSLEFT,True)
            print("Turn LEFT LEDS ON")
        else:
            GPIO.output(GPIO_LEDSLEFT,False)
            print("Turn LEFT LEDS OFF")
    
    w.update()
    w.update_idletasks()
