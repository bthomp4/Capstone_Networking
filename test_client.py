# This program is used for the testing the client side with the PiCamera & Sensors

from socket import *
import argparse

import signal
import sys
import subprocess

# for encoding the image 
import base64
from PIL import Image
from errno import *
from time import *

# for GPIO Pins (can only be tested on RPi)
import RPi.GPIO as GPIO

from picamera import PiCamera

# ------------------
# Defining Variables
# ------------------

# Set Variables
picture = "/ram/test.jpg"
DATA_SIZE = 500
SS_FlagSize = 4
SN_FlagSize = 4
DCNT_flag   = 0
measurementSleep = 0.00001
settleSleep      = 0.5
sideSensorRange  = 120
cp = 1 # check point divider value
encode_msgs = []
sys_mode = " " # mode of the system (FB or BS)
speedSound = 13500 # speed of sound in in/s

# Dictionaries for Flag Values
dictRec = {'0':"INIT_SYN",'1':"INIT_SYNACK",'2':"INIT_ACK",'3':"FULL_DATA_SYN",'4':"FULL_DATA_ACK",'5':"SYNC_SYN",'6':"SYNC_ACK",'7':"DATA_SYN",'8':"DATA_ACK",'9':"DATA_CAM",'A':"DATA_SEN",'B':"MODE_SYN",'C':"MODE_ACK",'D':"DCNT"}

dictSend = {"INIT_SYN":'0',"INIT_SYNACK":'1',"INIT_ACK":'2',"FULL_DATA_SYN":'3',"FULL_DATA_ACK":'4',"SYNC_SYN":'5',"SYNC_ACK":'6',"DATA_SYN":'7',"DATA_ACK":'8',"DATA_CAM":'9',"DATA_SEN":'A',"MODE_SYN":'B',"MODE_ACK":'C', "DCNT":'D'}

# GPIO pins (BCM) and their purpose
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER_LEFT  = 23
GPIO_ECHO_LEFT     = 24
GPIO_TRIGGER_RIGHT = 5
GPIO_ECHO_RIGHT    = 6
GPIO_SAFE_SD       = 3
GPIO_LBO           = 26 

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER_LEFT,GPIO.OUT) # Trigger LEFT
GPIO.setup(GPIO_ECHO_LEFT,GPIO.IN)     # Echo LEFT
GPIO.setup(GPIO_TRIGGER_RIGHT,GPIO.OUT) # Trigger RIGHT
GPIO.setup(GPIO_ECHO_RIGHT,GPIO.IN)     # ECHO RIGHT

# For handling Safe Shutdown and LBO
GPIO.setup(GPIO_SAFE_SD, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(GPIO_SAFE_SD, GPIO.FALLING)

GPIO.setup(GPIO_LBO, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(GPIO_LBO, GPIO.RISING)

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER_LEFT, False)
GPIO.output(GPIO_TRIGGER_RIGHT, False)


# -------------------
# Defining Functions
# -------------------

# -----------------------------------
# Takes a measurement from the sensor
# -----------------------------------
def TakeMeasurement(Trigger, Echo):
    GPIO.output(Trigger, True)
    sleep(measurementSleep)
    GPIO.output(Trigger, False)
    start = time()

    while GPIO.input(Echo) == 0:
        start = time()
    while GPIO.input(Echo) == 1:
        stop = time()
    stop = time()

    elapsed = stop - start 
    distance = (elapsed * speedSound/2)

    return distance 

# -----------
# encodeImage
# -----------
def encodeImage():
    #Compress the image
    cam_pic = Image.open(picture)
    
    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save("/ram/test2_scaled.jpg",quality=20) 

    with open("/ram/test2_scaled.jpg",'rb') as image:
        image_64_encode = base64.encodestring(image.read())

    return image_64_encode

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
        sleep(measurementSleep)
        if (leftMeasure < sideSensorRange):
            print(str(i) + "Left Measure" + str(leftMeasure))
            numPingLeft = numPingLeft + 1
        rightMeasure = TakeMeasurement(GPIO_TRIGGER_RIGHT, GPIO_ECHO_RIGHT)
        sleep(measurementSleep)
        if (rightMeasure < sideSensorRange):
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

# ------------------------------
# disconnect
# ------------------------------
def disconnect():
    print("Rear Unit Shutting Down")
    GPIO.cleanup()
    client_socket.close()
    #subprocess.call(['shutdown', '-h', 'now'], shell=False)

# ---------------
# Main Script
# ---------------

sleep(settleSleep)

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

# Remove later ------------------
def signal_handler(signal,frame):
    GPIO.cleanup()
    client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
# ------------------------------

# sending a message to initialize connection
message = dictSend["INIT_SYN"] + ",0001,0001,VOID"

message_received = False
client_socket.setblocking(False)
response = ""
serverAddress = 0

while not message_received:
    print("Sending INIT_SYN")
    client_socket.sendto(message.encode(),(args.server_name,server_port))
    try:
        message_received = True
        response, serverAddress = client_socket.recvfrom(2048)
    except error as e:
        if e.errno is 107 or e.errno is 11:
            message_received = False

client_socket.setblocking(True)
while True:

    # recieving message from server
    if not message_received:
        response,serverAddress = client_socket.recvfrom(2048)
    message_received = False
    splitPacket = response.split(b',')

    if GPIO.event_detected(GPIO_SAFE_SD) or GPIO.event_detected(GPIO_LBO):
        message = dictSend["DCNT"] + ",0001,0001,VOID"
        client_socket.sendto(message.encode(),(args.server_name,server_port))
        disconnect()

    if dictRec[splitPacket[0].decode()] == "INIT_SYNACK":
        # send back an INIT_ACK
        print("Received INIT_SYNACK, sending INIT_ACK")
        message = dictSend["INIT_ACK"] + ",0001,0001,VOID"
        client_socket.sendto(message.encode(),(args.server_name,server_port))
    elif dictRec[splitPacket[0].decode()] == "MODE_SYN":
        # Send back MODE_ACK
        print("Received MODE_SYN")
        sys_mode = splitPacket[3].decode()

        # When in Full Battery Mode, turn on Camera
        if (sys_mode == "FB"):
            print("Turn on Camera")
            camera = PiCamera()

        print("Sending MODE_ACK")
        message = dictSend["MODE_ACK"] + ",0001,0001," + sys_mode
        client_socket.sendto(message.encode(),(args.server_name,server_port))
    elif dictRec[splitPacket[0].decode()] == "SYNC_ACK":

        print("Received SYNC_ACK")

        data_type,SS = splitData(splitPacket[3])

        if data_type == "CAM":
            print("Handling Camera Data")
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
                packetInfo = dictSend["DATA_CAM"] + ',' + SS + ',' + SN + ','

                client_socket.sendto(packetInfo.encode() + data, (args.server_name,server_port))

                # if sent 1/8 of SS
                if (packet_count == check_point):

                    # reset the packet count
                    packet_count = 0

                    # sending Data_Syn to server
                    message = dictSend["DATA_SYN"] + ",0001,0001,CAM!" + SS
                    client_socket.sendto(message.encode(), (args.server_name,server_port))
                    # waiting to see if all packets have been recieved
                    response,serverAddress = client_socket.recvfrom(2048)
                    splitResponse = response.split(b',')

                    # Check if response was a disconnect message
                    if dictRec[splitPacket[0].decode()] == "DCNT":
                        disconnect()

                    data_type,other = splitData(splitResponse[3])

                    packet_lost = int(other)

                    while (packet_lost != -1):
                        for num_msg in range(packet_lost,(num_packet+ 1)):
                            data = encode_msgs[num_msg]
                            SN = str(num_msg)
                            if (len(SN) != SN_FlagSize):
                                for l in range(0,(SN_FlagSize + len(SN))):
                                    SN = '0' + SN
                            message = dictSend["DATA_CAM"] + ',' + SS + ',' + SN + ','
                            client_socket.sendto(message.encode() + data, (args.server_name, server_port))

                        # sending data syn to server
                        message = dictSend["DATA_SYN"] + ",0001,0001,CAM!" + SS
                        client_socket.sendto(message.encode(), (args.server_name,server_port))
                        response,serverAddress = client_socket.recvfrom(2048)
                        splitResponse = response.split(b',')


                        # Check if response was a disconnect message
                        if dictRec[splitPacket[0].decode()] == "DCNT":
                            disconnect()

                        data_type,other = splitData(splitResponse[3])

                        packet_lost = int(other)
                num_packet = num_packet + 1

            message = dictSend["FULL_DATA_SYN"] + ",0001,0001," + sys_mode + "!CAM"
            client_socket.sendto(message.encode(),(args.server_name,server_port))
        elif data_type == "SEN":
            print("Handling Sensor Data")
            # Send DATA_SEN message
            LS, RS = UpdateSideSensors()

            message = dictSend["DATA_SEN"] + ",0001,0001," + LS + '!' + RS
            client_socket.sendto(message.encode(), (args.server_name,server_port))

            # Send DATA_SYN
            print("Sending Data_SYN")
            message = dictSend["DATA_SYN"] + ",0001,0001,SEN!VOID"
            client_socket.sendto(message.encode(), (args.server_name,server_port))

            # Wait for DATA_ACK from Server
            print("Receiving DATA_ACK")
            response,serverAddress = client_socket.recvfrom(2048)
            
            # Check if response was a disconnect message
            if dictRec[splitPacket[0].decode()] == "DCNT":
                disconnect()

            # Then send a FULL_DATA_SYN
            print("Sending FULL_DATA_SYN")
            message = dictSend["FULL_DATA_SYN"] + ",0001,0001," + sys_mode + "!SEN"
            client_socket.sendto(message.encode(), (args.server_name,server_port))

    elif dictRec[splitPacket[0].decode()] == "FULL_DATA_ACK":

        print("Receiving FULL_DATA_ACK")

        sys_mode,data_type = splitData(splitPacket[3])

        if sys_mode == "FB":
            # Sending both camera and sensor data

            if data_type == "VOID" or data_type == "SEN":
                print("Taking Picture")
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
                message = dictSend["SYNC_SYN"] + ",0001,0001,CAM!" + SS
                client_socket.sendto(message.encode(), (args.server_name,server_port))
            elif data_type == "CAM":
                # send SYNC_SYN for SENSOR
                print("Sending SYNC_SYN for Sensor DATA")

                message = dictSend["SYNC_SYN"] + ",0001,0001,SEN!1"
                client_socket.sendto(message.encode(), (args.server_name,server_port))
        elif sys_mode == "BS":
            print("in BS mode, Sending SYNC_SYN for Sensor Data")
            # Only sending sensor data since display is turned off
            message = dictSend["SYNC_SYN"] + ",0001,0001,SEN!1"
            client_socket.sendto(message.encode(), (args.server_name,server_port))

    elif dictRec[splitPacket[0].decode()] == "DCNT":
        print("Handling a DCNT from the server")
        disconnect()

# Rear Unit Shutting down
# -----------------------------------------------------
#print("Rear Unit Shutting Down")
#GPIO.cleanup()
#client_socket.close()
#subprocess.call(['shutdown', '-h', 'now'], shell=False)
# -----------------------------------------------------
