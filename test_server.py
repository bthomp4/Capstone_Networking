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

# ---------------
# Main Script
# ---------------

# Set variables
HasLost = False
VOID_DATA = "VOID"

picture = "test_decode.jpg"

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

# GPIO pins and their purpose
GPIO_TRIGGER    = 23
GPIO_ECHO       = 20
GPIO_LEDSRIGHT  = 21
GPIO_LEDSLEFT   = 27

# not needed yet, only testing side sensors
#GPIO_FRONTLED1  = 2
#GPIO_FRONTLED2  = 3
#GPIO_FRONTLED3  = 4
#GPIO_FRONTLED4  = 17
#GPIO_FRONTLED5  = 27
#GPIO_FRONTLED6  = 22
#GPIO_FRONTLED7  = 10
#GPIO_FRONTLED8  = 9
#GPIO_FRONTLED9  = 11
#GPIO_FRONTLED10 = 0

# Setting up socket
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

def signal_handler(signal,frame):
    GPIO.cleanup()
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Setting up gui for displaying image
w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()

sys_mode = " "

# begin loop
while True:

    # for testing dropped packets
    response, clientAddress = serverSocket.recvfrom(2048)
    splitPacket = response.split(b',')

    if dictRec[splitPacket[0].decode()] == 'INIT_SYN':
        # send back INIT_SYNACK
        message = dictSend['INIT_SYNACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + VOID_DATA
        
        serverSocket.sendto(message.encode(),clientAddress) 
    elif dictRec[splitPacket[0].decode()] == 'INIT_ACK':
        # Send back MODE_SYN
        # For testing purposes, just do Full Battery for now
        sys_mode = "FB"
        message = dictSend['MODE_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + sys_mode
        serverSocket.sendto(message.encode(),clientAddress)        

        # Wait for MODE_ACK, DATA = "MODE"
        response, clientAddress = serverSocket.recvfrom(2048)

        # send back FULL_DATA_ACK, DATA = "MODE!VOID"
        msg_data = sys_mode + '!' + VOID_DATA
        message = dictSend['FULL_DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + msg_data 

        serverSocket.sendto(message.encode(),clientAddress) 
    elif dictRec[splitPacket[0].decode()] == 'FULL_DATA_SYN':
        
        sys_mode,data_type = splitData(splitPacket[3])

        if data_type == "CAM":
            print("Client done sending all packets for image")
            
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
            # For now, just send back a FULL_DATA_ACK
            msg_data = sys_mode + '!' + "SEN"

            message = dictSend['FULL_DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + msg_data
            serverSocket.sendto(message.encode(),clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'SYNC_SYN':
                
        data_type,SS = splitData(splitPacket[3])
        SegmentSize = int(SS)

        msg_data = data_type + '!' + SS

        message = dictSend['SYNC_ACK'] + "," + MSS_1 + ',' + SN_1 + ',' + msg_data
        serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'DATA_SYN':
        
        data_type,other_data = splitData(splitPacket[3])

        if data_type == "CAM": 
            #check for packet loss
            print("Checking for packet loss")

            SegmentSize = int(other_data)

            packet_dropped = check_point(SegmentSize)
       
            if (packet_dropped == -1):
                HasLost = False
                check_pt = check_pt + (SegmentSize//8) 
            else:
                HasLost = True
        elif data_type == "SEN":
            print("Recieved Data_SYN for Sensor Data")
            
            message = dictSend['DATA_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + "SEN!VOID"
            serverSocket.sendto(message.encode(), clientAddress)

    elif dictRec[splitPacket[0].decode()] == 'DATA_CAM':

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

        print("Appending SegmentNum : " + str(SegmentNum))
    
    elif dictRec[splitPacket[0].decode()] == 'DATA_SEN':
        # handle the sensor data
        print("Recieving sensor data")
    
        LeftSensor,RightSensor = splitData(splitPacket[3])
        
        # Left Sensor Data
        LS = int(LeftSensor)
        
        # Right Sensor Data
        RS = int(RightSensor)

        if RS <= 120: 
            #GPIO.output(GPIO_LEDSRIGHT,True)
            print("Turn Right LEDS ON")
        else:
            #GPIO.output(GPIO_LEDSRIGHT,False)
            print("Turn Right LEDS OFF")
        if LS <= 120:
            #GPIO.output(GPIO_LEDSLEFT,True)
            print("Turn LEFT LEDS ON")
        else:
            #GPIO.output(GPIO_LEDSLEFT,False)
            print("Turn LEFT LEDS OFF")
    
    w.update()
    w.update_idletasks()
