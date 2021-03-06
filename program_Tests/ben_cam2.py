# This program is used for the testing the client side with just PiCamera

from socket import *
import argparse

import signal
import sys

# for encoding the image 
import base64
from PIL import Image

from time import *

from picamera import PiCamera

# -------------------
# Defining Functions
# -------------------

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

# Set file names
picture = "test.jpg"

# Set variables
DATA_SIZE   = 1500
VOID_DATA   = "VOID"
SS_FlagSize = 4
SN_FlagSize = 4
DCNT_flag   = 0

# Dictionaries for Flag Values
dictRec = {'0':'INIT_SYN','1':'INIT_SYNACK','2':'INIT_ACK','3':'0','4':'FULL_DATA_ACK','5':'SYNC_SYN','6':'SYNC_ACK','7':'DATA_SYN','8':'DATA_ACK','9':'DATA_CAM','A':'DATA_SEN','B':'MODE_SYN','C':'MODE_ACK'}

dictSend = {'INIT_SYN':'0','INIT_SYNACK':'1','INIT_ACK':'2','0':'3','FULL_DATA_ACK':'4','SYNC_SYN':'5','SYNC_ACK':'6','DATA_SYN':'7','DATA_ACK':'8','DATA_CAM':'9','DATA_SEN':'A','MODE_SYN':'B','MODE_ACK':'C'}

# check point divider value
cp = 1

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
    client_socket.close()
    print("full: " + str(sum(times)/len(times)))
    print("loop: " + str(sum(loop)/len(loop)))
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
    # capture picture    
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
    message = SS 
    client_socket.sendto(message.encode(), (args.server_name,server_port))
    packet_count = 0
    num_packet = 0



    while(num_packet < len(encode_msgs)):

        packet_count = packet_count + 1
        data = encode_msgs[num_packet]

        # Sending Camera Data
        client_socket.sendto(data, (args.server_name,server_port))
        num_packet = num_packet + 1

    message = "end_data_sync" 
    lstart = time()
    client_socket.sendto(message.encode(),(args.server_name,server_port))

    # recieving message from server
    response,serverAddress = client_socket.recvfrom(2048)
    lstop = time()
    loop.append(lstop - lstart)
    
    stop = time()
    print("end process")
    times.append(stop - start)
