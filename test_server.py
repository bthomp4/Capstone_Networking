from socket import *
from errno import *

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

noConnect = True   # Boolean for stating connection of a client
HasLost = False    # Boolean for packet loss
FrontLEDs = 0
settleModule_sleep = 0.5
takeMeasurement_sleep = 0.00001
MSS = 9999    # Max Segment Size
encode_string = []    # holds encoded string from client
picture = "test_decode.jpg"
logo = "logo.jpg"
check_pt = 0    # where packets need to be checked for loss 
cp_value = 1    # SS/cp_value = num of packets sent per check
packetsRec = [0] * MSS    # stores packets that have been received

# Dictionaries for Flag Values
dictRec = {'0':'INIT_SYN','1':'INIT_SYNACK','2':'INIT_ACK','3':'FULL_DATA_SYN','4':'FULL_DATA_ACK','5':'SYNC_SYN','6':'SYNC_ACK','7':'DATA_SYN','8':'DATA_ACK','9':'DATA_CAM','A':'DATA_SEN','B':'MODE_SYN','C':'MODE_ACK', 'D':'DCNT'}

dictSend = {'INIT_SYN':'0','INIT_SYNACK':'1','INIT_ACK':'2','FULL_DATA_SYN':'3','FULL_DATA_ACK':'4','SYNC_SYN':'5','SYNC_ACK':'6','DATA_SYN':'7','DATA_ACK':'8','DATA_CAM':'9','DATA_SEN':'A','MODE_SYN':'B','MODE_ACK':'C','DCNT':'D'}

# GPIO pins (BCM) and their purpose
GPIO.setmode(GPIO.BCM)
GPIO_ModeSel       = 16
GPIO_lidarTrig     = 23
GPIO_lidarEcho     = 20
GPIO_LEDSRIGHT     = 21
GPIO_LEDSLEFT      = 27
GPIO_LEDSel0       = 2
GPIO_LEDSel1       = 14
GPIO_LEDSel2       = 4    #MSB
GPIO_LEDEn         = 17
##GPIO_LEDStatus    = 11
##GPIO_SafeSD       = 3
##GPIO_LBO          = 26

# Set pins as output and input
GPIO.setup(GPIO_ModeSel,GPIO.IN)
GPIO.setup(GPIO_lidarTrig,GPIO.OUT)
GPIO.setup(GPIO_lidarEcho,GPIO.IN)
GPIO.setup(GPIO_LEDSRIGHT,GPIO.OUT)
GPIO.setup(GPIO_LEDSLEFT,GPIO.OUT)
GPIO.setup(GPIO_LEDSel0,GPIO.OUT)
GPIO.setup(GPIO_LEDSel1,GPIO.OUT)
GPIO.setup(GPIO_LEDSel2,GPIO.OUT)
GPIO.setup(GPIO_LEDEn,GPIO.OUT)
##GPIO.setup(GPIO_LEDStatus, GPIO.OUT)
##GPIO.setup(GPIO_SafeSD, GPIO.IN)
##GPIO.setup(GPIO_LBO, GPIO.IN)

GPIO.output(GPIO_lidarTrig,False)
GPIO.output(GPIO_LEDSRIGHT, False)
GPIO.output(GPIO_LEDSLEFT, False)
GPIO.output(GPIO_LEDSel0, False)
GPIO.output(GPIO_LEDSel1, False)
GPIO.output(GPIO_LEDSel2, False)
GPIO.output(GPIO_LEDEn, False)
##GPIO.output(GPIO_LEDStatus, False)

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
    for i in range (check_pt,(check_pt + (SegmentSize//cp_value))):
        if packetsRec[i] == 0:
            packet_dropped = i
            break
    data = "CAM" + '!' + str(packet_dropped)

    # Sending DATA_ACK
    message = dictSend['DATA_ACK'] + ',0001,0001,' + data

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
    GPIO.output(GPIO_lidarTrig, True)
    # Wait 10us
    sleep(takeMeasurement_sleep)
    GPIO.output(GPIO_lidarTrig, False)
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

# -----------------------------------------
# UpdateLidar takes 'n' measurements and
# sets the value for the number of LEDs to
# be turned on.
# -----------------------------------------
def UpdateLidar():
    global FrontLEDs

    n = 3 # num of measurements taken

    listDist = []
    for i in range(0,n):
        listDist.append(MeasureLidar())

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

# ---------------
# Main Script
# ---------------

sleep(settleModule_sleep)

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
#sys_mode = "FB"

if GPIO.input(GPIO_ModeSel):
    sys_mode = "FB"
else:
    sys_mode = "BS"


serverSocket.setblocking(False) # to allow for the loop to process
# Initial Handshaking loop
while noConnect:
    print("Waiting for connection")
    print("Flash LED")
    try:
        message_rec = True
        response, clientAddress = serverSocket.recvfrom(2048)
    except error as e:
        if e.errno is 107 or e.errno is 11:
            print("Nothing in socket")
            message_rec = False
    if message_rec:

        splitPacket = response.split(b',')
        print(dictRec[splitPacket[0].decode()])

        if dictRec[splitPacket[0].decode()] == 'INIT_SYN':
            # send back INIT_SYNACK
            message = dictSend['INIT_SYNACK'] + ',0001,0001,VOID'
        
            serverSocket.sendto(message.encode(),clientAddress) 
        elif dictRec[splitPacket[0].decode()] == 'INIT_ACK':
            # Send back MODE_SYN
            message = dictSend['MODE_SYN'] + ',0001,0001,' + sys_mode
            serverSocket.sendto(message.encode(),clientAddress)        
            print("Sent MODE_SYN")
            noConnect = False
            message = "Connected"
            serverSocket.setblocking(True)
            # Wait for MODE_ACK, DATA = "MODE"
            response, clientAddress = serverSocket.recvfrom(2048)
            print("Received MODE_ACK")

            # send back FULL_DATA_ACK, DATA = "MODE!VOID"
            msg_data = sys_mode + '!VOID'
            message = dictSend['FULL_DATA_ACK'] + ',0001,0001,' + msg_data 

            serverSocket.sendto(message.encode(),clientAddress) 



# begin loop
while True:

    response, clientAddress = serverSocket.recvfrom(2048)
    splitPacket = response.split(b',')
    print(dictRec[splitPacket[0].decode()])

    if dictRec[splitPacket[0].decode()] == 'FULL_DATA_SYN':
        
        sys_mode,data_type = splitData(splitPacket[3])

        if data_type == "CAM":
            
            #reset values 
            check_pt = 0
            packetsRec = [0] * MSS        

            full_string = b''
            i = 0

            while(i < len(encode_string)):
                full_string = full_string + encode_string[i]
                i = i + 1
        
            decode_string(full_string)

            message = dictSend['FULL_DATA_ACK'] + ",0001,0001," + sys_mode + "!CAM"
            serverSocket.sendto(message.encode(),clientAddress)
        elif data_type == "SEN":

            message = dictSend['FULL_DATA_ACK'] + ",0001,0001," + sys_mode + "!SEN"
            serverSocket.sendto(message.encode(),clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'SYNC_SYN':
                
        data_type,SS = splitData(splitPacket[3])
        SegmentSize = int(SS)

        msg_data = data_type + '!' + SS

        message = dictSend['SYNC_ACK'] + ",0001,0001," + msg_data
        serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'DATA_SYN':
        
        data_type,other_data = splitData(splitPacket[3])

        if data_type == "CAM": 
            #check for packet loss

            SegmentSize = int(other_data)

            packet_dropped = check_point(SegmentSize)
       
            if (packet_dropped == -1):
                HasLost = False
                check_pt = check_pt + (SegmentSize//cp_value) 
            else:
                HasLost = True
        elif data_type == "SEN":
            message = dictSend['DATA_ACK'] + ",0001,0001,SEN!VOID"
            serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'DATA_CAM':

        SegmentSize = int(splitPacket[1])
        SegmentNum = int(splitPacket[2]) 
       
        packetsRec[SegmentNum] = 1

        # Append the encoded image data 
        if (SegmentNum == len(encode_string) or HasLost == False):
            encode_string.append(splitPacket[3])
        else:
            encode_string[SegmentNum] = splitPacket[3]

    elif dictRec[splitPacket[0].decode()] == 'DATA_SEN':
    
        LS,RS = splitData(splitPacket[3])

        #UpdateLidar()

        # just for testing
        FrontLEDs = 6
        
        if FrontLEDs == 0:
            print("Not enabled")
            GPIO.output(GPIO_LEDSel0, False)
            GPIO.output(GPIO_LEDSel1, False)
            GPIO.output(GPIO_LEDSel2, False)
            GPIO.output(GPIO_LEDEn, False)
        elif FrontLEDs == 1:
            print("One LED on")
            GPIO.output(GPIO_LEDSel0, False)
            GPIO.output(GPIO_LEDSel1, False)
            GPIO.output(GPIO_LEDSel2, False)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 2:
            print("Two LEDs on")
            GPIO.output(GPIO_LEDSel0, True)
            GPIO.output(GPIO_LEDSel1, False)
            GPIO.output(GPIO_LEDSel2, False)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 3:
            print("Three LEDs on")
            GPIO.output(GPIO_LEDSel0, False)
            GPIO.output(GPIO_LEDSel1, True)
            GPIO.output(GPIO_LEDSel2, False)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 4:
            print("Four LEDs on")
            GPIO.output(GPIO_LEDSel0, True)
            GPIO.output(GPIO_LEDSel1, True)
            GPIO.output(GPIO_LEDSel2, False)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 5:
            print("Five LEDs on")
            GPIO.output(GPIO_LEDSel0, False)
            GPIO.output(GPIO_LEDSel1, False)
            GPIO.output(GPIO_LEDSel2, True)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 6:
            print("Six LEDs on")
            GPIO.output(GPIO_LEDSel0, True)
            GPIO.output(GPIO_LEDSel1, False)
            GPIO.output(GPIO_LEDSel2, True)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 7:
            print("Seven LEDs on")
            GPIO.output(GPIO_LEDSel0, False)
            GPIO.output(GPIO_LEDSel1, True)
            GPIO.output(GPIO_LEDSel2, True)
            GPIO.output(GPIO_LEDEn, True)
        elif FrontLEDs == 8:
            print("Eight LEDs on")
            GPIO.output(GPIO_LEDSel0, True)
            GPIO.output(GPIO_LEDSel1, True)
            GPIO.output(GPIO_LEDSel2, True)
            GPIO.output(GPIO_LEDEn, True)

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
    
    elif dictRec[splitPacket[0].decode()] == 'DCNT':
        # Handle Disconnect from Client
        # Turn on Status LED if Disconnect (set True)
        # Turn off Status LED if Disconnect (set False)
        print("Handle DCNT")
    

    w.update()
    w.update_idletasks()
