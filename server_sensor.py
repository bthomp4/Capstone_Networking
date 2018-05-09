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
# -----------------

packetsRec = [0] * MSS

# Dictionaries for Flag Values
dictRec = {'0':'INIT_SYN','1':'INIT_SYNACK','2':'INIT_ACK','3':'FULL_DATA_SYN','4':'FULL_DATA_ACK','5':'SYNC_SYN','6':'SYNC_ACK','7':'DATA_SYN','8':'DATA_ACK','9':'DATA_CAM','A':'DATA_SEN','B':'MODE_SYN','C':'MODE_ACK'}

dictSend = {'INIT_SYN':'0','INIT_SYNACK':'1','INIT_ACK':'2','FULL_DATA_SYN':'3','FULL_DATA_ACK':'4','SYNC_SYN':'5','SYNC_ACK':'6','DATA_SYN':'7','DATA_ACK':'8','DATA_CAM':'9','DATA_SEN':'A','MODE_SYN':'B','MODE_ACK':'C'}

# ------------------
# Defining Functions
# ------------------

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

# Setting up socket
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

def signal_handler(signal,frame):
    GPIO.cleanup()
    serverSocket.close()
    print("full: " + str(sum(times)/len(times)))
    print("loop: " + str(sum(loop)/len(loop)))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# begin loop
while True:

    print("start process")
    start = time()

    print("Receiving Data_Sen")
    response, clientAddress = serverSocket.recvfrom(2048)
    print(response.decode())

    print("Receiving Data_Syn")
    response, clientAddress = serverSocket.recvfrom(2048)
    print(response.decode())

    print("Sending Data_Ack")
    message = "Got Data_Ack"
    serverSocket.sendto(message.encode(), (args.server_name, server_port))        

    lstart = time()
    response, clientAddress = serverSocket.recvfrom(2048)
    print(response.encode())
    print("Received FULL_DATA_SYN")
    message = "Thanks for the data"
    serverSocket.sendto(message.encode(),clientAddress)
    lstop = time()
    loop.append(lstop - lstart)
   
    stop = time()
    print("end process")
    times.append(stop - start) 
