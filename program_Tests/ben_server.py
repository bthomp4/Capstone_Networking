from socket import *

# for decoding and displaying the image
import base64
from PIL import Image,ImageTk
import tkinter

from time import *

import signal
import sys

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

picture = "/ram/test_decode.jpg"

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

# Setting up socket
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

def signal_handler(signal,frame):
    serverSocket.close()
    print("full: " + str(sum(times)/len(times)))
    print("loop: " + str(sum(loop)/len(loop)))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Setting up gui for displaying image
w = tkinter.Tk()
im = Image.open('logo.jpg')
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()

sys_mode = " "

# begin loop
lost = 0

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
    # for testing dropped packets
    response, clientAddress = serverSocket.recvfrom(2048)
    print("recieved number of messages")

    num_segs = response.decode()
    print("Num_segs: " + num_segs)

    packet_num = 0
    flag = True
    messages = b""
    while packet_num < int(num_segs):
        response, clientAddress = serverSocket.recvfrom(2048)
        if response == "end_data_sync":
            print("oops, lost something!")
            lost = lost + 1
            flag = False
            break
        else:
            messages = messages + response
        packet_num = packet_num + 1
    lstart = time()
    decode_string(messages)
    lstop = time()
    if flag:
        response, clientAddress = serverSocket.recvfrom(2048)
    message = "hi"
    serverSocket.sendto(message.encode(),clientAddress)
    loop.append(lstop - lstart)
    
    w.update()
    w.update_idletasks()

    stop = time()
    print("end process")
    times.append(stop - start)
