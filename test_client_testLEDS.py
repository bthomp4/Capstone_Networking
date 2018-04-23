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

# -------------------
# Defining Functions
# -------------------

# --------------------------------------------------
# measure1 takes a measurement from the first sensor
# --------------------------------------------------
def measure1():
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

    elapsed = stop-start
    distance = (elasped * speedSound/2)

    return distance

# ----------------------------------------------------
# measure_average1 finds the average of 3 measurements
# ----------------------------------------------------
def measure_average1():
    # This function takes 3 measurements and
    # returns the average.

    distance1 = measure1()
    sleep(0.1)
    distance2 = measure1()
    sleep(0.1)
    distance3 = measure1()
    distance = distance1 + distance2 + distance3
    distance = distance/3
    return distance

# ---------------------------------------------------
# measure2 takes a measurement from the second sensor
# ---------------------------------------------------
def measure2():
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

    elapsed = stop-start
    distance = (elapsed * speedSound)/2

    return distance

# ----------------------------------------------------
# measure_average2 finds the average of 3 measurements
# ----------------------------------------------------
def measure_average2():
    # This function takes 3 measurements and
    # returns the average.

    distance1 = measure2()
    sleep(0.1)
    distance2 = measure2()
    sleep(0.1)
    distance3 = measure2()
    distance = distance1 + distance2 + distance3
    distance = distance/3

    return distance

# -----------
# encodeImage
# -----------
def encodeImage():
    #Compress the image
    cam_pic = Image.open(picture)
    
    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save("test2_scaled.jpg",quality=20) 

    with open("test2_scaled.jpg",'rb') as image:
        image_64_encode = base64.encodestring(image.read())

    return image_64_encode

# ------------------------------------------------------------------
# UpdateSideSensors updates the sensor values and returns the values
# ------------------------------------------------------------------
def UpdateSideSensors():

    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER1,False)
    GPIO.output(GPIO_TRIGGER2,False)

    sleep(0.5)
    distance1 = measure_average1()
    distance2 = measure_average2()

    return distance1, distance2

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
dictRec = {'0':'INIT_SYN','1':'INIT_SYNACK','2':'INIT_ACK','3':'FULL_DATA_SYN','4':
'FULL_DATA_ACK','5':'SYNC_SYN','6':'SYNC_ACK','7':'DATA_SYN','8':'DATA_ACK','9':'DA
TA_CAM','A':'DATA_SEN','B':'MODE_SYN','C':'MODE_ACK'}

dictSend = {'INIT_SYN':'0','INIT_SYNACK':'1','INIT_ACK':'2','FULL_DATA_SYN':'3','FU
LL_DATA_ACK':'4','SYNC_SYN':'5','SYNC_ACK':'6','DATA_SYN':'7','DATA_ACK':'8','DATA_
CAM':'9','DATA_SEN':'A','MODE_SYN':'B','MODE_ACK':'C'}

# check point divider value
cp = 8

# initialize encode_msgs list
encode_msgs = []

# for the mode of the system, FB or BS
sys_mode = " "

camera = PiCamera()

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

# sending a message to initialize connection
message = dictSend['INIT_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + VOID_DATA

client_socket.sendto(message.encode(),(args.server_name,server_port))

while True:

    # recieving message from server
    response,serverAddress = client_socket.recvfrom(2048)
    splitPacket = response.split(b',')

    if dictRec[splitPacket[0].decode()] == 'INIT_SYNACK':
        # send back an INIT_ACK
        message = dictSend['INIT_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + VOID_DATA
        client_socket.sendto(message.encode(),(args.server_name,server_port))
    elif dictRec[splitPacket[0].decode()] == 'MODE_SYN':
        # Send back MODE_ACK
        sys_mode = splitPacket[3].decode()
        message = dictSend['MODE_ACK'] + ',' + MSS_1 + ',' + SN_1 + ',' + sys_mode
        client_socket.sendto(message.encode(),(args.server_name,server_port))
    elif dictRec[splitPacket[0].decode()] == 'SYNC_ACK':

        data_type,SS = splitData(splitPacket[3])

        if data_type == "CAM":
            packet_count = 0
            num_packet = 0

            check_point = (int(SS)//cp)

            while(num_packet < len(encode_msgs)):

                packet_count = packet_count + 1
                data = encode_msgs[num_packet]

                # Segment Number
                SN = str(num_packet)

                # pad segment number to be 4 bytes
                if (len(SN) != SN_FlagSize):
                    for l in range(0,(SN_FlagSize - len(SN))):
                        SN = '0' + SN

                # Sending Camera Data
                packetInfo = dictSend['DATA_CAM'] + ',' + SS + ',' + SN + ','

                client_socket.sendto(packetInfo.encode() + data, (args.server_name,
server_port))

                # if sent 1/8 of SS
                if (packet_count == check_point):

                    # reset the packet count
                    packet_count = 0

                    # sending Data_Syn to server
                    msg_data = "CAM!" + SS
                    message = dictSend['DATA_SYN'] + ',' + MSS_1 + ',' + SN_1 + ','
 + msg_data
                    client_socket.sendto(message.encode(), (args.server_name,server
_port))
                    # waiting to see if all packets have been recieved
                    response,serverAddress = client_socket.recvfrom(2048)
                    splitResponse = response.split(b',')

                    data_type,other = splitData(splitResponse[3])

                    packet_lost = int(other)

                    while (packet_lost != -1):
                        for num_msg in range(packet_lost,(num_packet+ 1)):
                            data = encode_msgs[num_msg]
                            SN = str(num_msg)
                            if (len(SN) != SN_FlagSize):
                                for l in range(0,(SN_FlagSize + len(SN))):
                                    SN = '0' + SN
                            message = dictSend['DATA_CAM'] + ',' + SS + ',' + SN +
','
                            client_socket.sendto(message.encode() + data, (args.ser
ver_name, server_port))

                        # sending data syn to server
                        msg_data = "CAM!" + SS
                        message = dictSend['DATA_SYN'] + ',' + MSS_1 + ',' + SN_1 +
 ',' + msg_data
                        client_socket.sendto(message.encode(), (args.server_name,se
rver_port))
                        response,serverAddress = client_socket.recvfrom(2048)
                        splitResponse = response.split(b',')

                        data_type,other = splitData(splitResponse[3])

                        packet_lost = int(other)
                num_packet = num_packet + 1

            msg_data = sys_mode + '!' + "CAM"
            message = dictSend['FULL_DATA_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' +
msg_data
            client_socket.sendto(message.encode(),(args.server_name,server_port))
        elif data_type == "SEN":
            # Send DATA_SEN message
            LS, RS = UpdateSideSensors()

            msg_data = str(LS) + '!' + str(RS)

            message = dictSend['DATA_SEN'] + ',' + MSS_1 + ',' + SN_1 + ',' + msg_d
ata
            client_socket.sendto(message.encode(), (args.server_name,server_port))

            # Send DATA_SYN
            message = dictSend['DATA_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + "SEN!
VOID"
            client_socket.sendto(message.encode(), (args.server_name,server_port))

            # Wait for DATA_ACK from Server
            response,serverAddress = client_socket.recvfrom(2048)

            # Then send a FULL_DATA_SYN
            msg_data = sys_mode + '!' + "SEN"
            message = dictSend['FULL_DATA_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' +
msg_data
            client_socket.sendto(message.encode(), (args.server_name,server_port))

    elif dictRec[splitPacket[0].decode()] == 'FULL_DATA_ACK':

        sys_mode,data_type = splitData(splitPacket[3])

        if sys_mode == "FB":
            # Sending both camera and sensor data

            if data_type == "VOID" or data_type == "SEN":
                camera.capture(picture)

                string = encodeImage()

                encode_msgs = []

                while string:
                    encode_msgs.append(string[:DATA_SIZE])
                    string = string[DATA_SIZE:]

                # segment size
                SS = str(len(encode_msgs))

                # pad segment size to be 4 bytes
                if (len(SS) != SS_FlagSize):
                    for i in range(0,(SS_FlagSize - len(SS))):
                        SS = '0' + SS

                #Sending SYNC_SYN message
                msg_data = "CAM" + '!' + SS
                message = dictSend['SYNC_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + m
sg_data

                client_socket.sendto(message.encode(), (args.server_name,server_por
t))
            elif data_type == "CAM":
                # send SYNC_SYN for SENSOR

                message = dictSend['SYNC_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + "
SEN!1"
                client_socket.sendto(message.encode(), (args.server_name,server_por
t))
        elif sys_mode == "BS":
            # Only sending sensor data since display is turned off
            message = dictSend['SYNC_SYN'] + ',' + MSS_1 + ',' + SN_1 + ',' + "SEN!
1"
client_socket.close()
