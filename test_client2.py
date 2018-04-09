# This program is used for testing the client program without using the PiCamera

# to bring in the print function from Python3
#from __future__ import print_function

from socket import *
import argparse

# for encoding the image 
import base64
from PIL import Image

# for displaying the time
from datetime import datetime

from time import *

# for GPIO Pins
import RPi.GPIO as GPIO

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
    # Compress the image
    cam_pic = Image.open(picture)

    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save(scaledPic,quality=20) 

    with open(scaledPic,'rb') as image:
        image_64_encode = base64.encodestring(image.read())

    print(image_64_encode)

    return image_64_encode

# ------------------------------------------------------------------
# UpdateSideSensors updates the sensor values and returns the values
# ------------------------------------------------------------------

def UpdateSideSensors():
    GPIO.output(GPIO_TRIGGER1,False)
    GPIO.output(GPIO_TRIGGER2,False)

    distance1 = measure_average1()
    distance2 = measure_average2()

    return distance1, distance2

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
picture = "tempPic.jpg"
scaledPic = "pic_scaled.jpg"

# Set variables
DATA_SIZE   = 500
MSS_1	    = 0001
SN_1        = 0001
VOID_DATA   = "VOID"
SS_FlagSize = 4
SN_FlagSize = 4

# Set Flag Values
INIT_SYN      = 1
INIT_SYNACK   = 2
INIT_ACK      = 3
FULL_DATA_SYN = 4
FULL_DATA_ACK = 5
SYNC_SYN      = 6
SYNC_ACK      = 7
DATA_SYN      = 8
DATA_ACK      = 9
DATA_CAM      = 10
DATA_SEN      = 11
MODE_SYN      = 12
MODE_ACK      = 13

# for testing dropped packets
drop_packets = [0,1,2,3,4,5,6,7]
#drop_packets = []

# initialize encode_msgs list
encode_msgs = []

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

# sending a message to initialize connection
message = str(INIT_SYN) + ',' + str(MSS_1) + ',' + VOID_DATA 

client_socket.sendto(message.encode(),(args.server_name,server_port)

while True:

    # recieving message from server
    response,serverAddress = client_socket.recvfrom(2048)
    splitPacket = response.split(b',')

    if int(splitPacket[0].decode()) == INIT_SYNACK:
        #send back an ACK
        print("Sending back an ACK")
    else if int(splitPacket[0].decode()) == SYNC_ACK:

        data = splitPacket[3].decode()
        splitData = data.split('!')
        data_flag = int(splitData[0])
        SS = splitData[1]  

        if data_flag == DATA_CAM:
            packet_count = 0
            num_packet = 0

            check_point = (int(SS)//8)
            print("Check_point value" + str(check_point))

            while(num_packet < len(encode_msgs)):		
        
                packet_count = packet_count + 1
                print("Segment Number (starting at 0) " + str(num_packet))
                # remove later --------
                if num_packet not in drop_packets:
                # remove later --------
                    data = encode_msgs[num_packet]

                    # Segment Number
                    SN = str(num_packet)

                    # pad segment number to be 4 bytes
                    if (len(SN) != SN_FlagSize):
                        for l in range(0,(SN_FlagSize - len(SN))):
                            SN = '0' + SN

                    # DATA_CAM Flag == 5
                    packetInfo = '5,' + SS + ',' + SN + ',' 

                    print("Sending Packet to Server")
                    client_socket.sendto(packetInfo.encode() + data, (args.server_name,server_port))
            
                # if sent 1/8 of SS
                print("Packet_count: " + str(packet_count))
                if (packet_count == check_point):		
                    print("Packet_count == check_point")
            
                    # reset the packet count
                    packet_count = 0 
                
                    # sending data syn == 10 to server
                    print("Sending Data Syn to Server")
                    dataSyn_msg = "10,1,1,void"
                    client_socket.sendto(dataSyn_msg.encode(), (args.server_name,server_port))
                    # waiting to see if all packets have been recieved
                    print("Waiting for server to send ACK message")
                    server_message,serverAddress = client_socket.recvfrom(2048)

                    packet_lost = int(server_message.decode())
                    print("Printing value of packet_lost " + str(packet_lost))

                    while (packet_lost != -1):
                        print("OH NO, WE LOST A PACKET!!!!")
                        print("Packet_Lost: " + str(packet_lost))
                        for num_msg in range(packet_lost,(num_packet+ 1)):
                            print("Segment Num being sent: " + str(num_msg))
                            data = encode_msgs[num_msg]
                            SN = str(num_msg)
                            if (len(SN) != SN_FlagSize):
                                for l in range(0,(SN_FlagSize + len(SN))):
                                    SN = '0' + SN
                            packetInfo = '5,' + SS + ',' + SN + ','
                            print("Sending Packet to Server")
                            client_socket.sendto(packetInfo.encode() + data, (args.server_name, server_port))
                     
                        # sending data syn to server
                        print("Sending Data Syn to Server")
                        dataSyn_msg = "10,1,1,void"
                        client_socket.sendto(dataSyn_msg.encode(), (args.server_name,server_port))

                        print("Waiting for server to send ACK message")
                        server_message,serverAddress = client_socket.recvfrom(2048)


                        packet_lost = int(server_message.decode())                
                
                num_packet = num_packet + 1

            print("sending done msg to server")
            dataSyn_message = "1,1,1,void"

            client_socket.sendto(dataSyn_message.encode(),(args.server_name,server_port))
    else if int(splitPacket[0].decode()) == FULL_DATA_ACK:
        if splitPacket[3].decode() == "VOID" or splitPacket[3].decode() == "SENSOR":
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
            syncSyn_data = str(DATA_CAM) + '!' + SS
            message = str(SYNC_SYN) + ',' + str(MSS_1) + ',' + str(MSS_1) + ',' + syncSyn_data

            client_socket.sendto(message.encode(), (args.server_name,server_port))

        else if splitPacket[3].decode() == "CAMERA":
            print("Sending Sensor data")

client_socket.close()
