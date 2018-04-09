from socket import *

# for decoding and displaying the image
import base64
from PIL import Image,ImageTk
import tkinter

from time import sleep

# for displaying the time
#from datetime import datetime

# starts out blank in beginning of program
picture = "test_decode.jpg"

# array to hold encoded string from client
encode_string = []

# Max Segment Size
MSS = 9999

# where packets need to be checked for loss
check_pt = 0

# List for storing which packets have been received
packetsRec = [0] * MSS

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

#Function Name: decode_string
#Usage: Decodes the image from the client
def decode_string(image_64_encode):
    global encode_string
    encode_string = []
    image_64_decode = base64.decodestring(image_64_encode)
    with open(picture,'wb') as image_result:
        image_result.write(image_64_decode)
    update_image()

def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open(picture))
    label.config(image = camImg)
    label.pack()

def check_point(SegmentSize):
    global check_pt
    global packetsRec

    print("Check_Pt: " + str(check_pt))
    packet_dropped = -1
    for i in range (check_pt,(check_pt + (SegmentSize//8))):
        if packetsRec[i] == 0:
            packet_dropped = i
            break
    packetDrop_msg = str(packet_dropped)
    serverSocket.sendto(packetDrop_msg.encode(),clientAddress)
    
    return packet_dropped

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()

HasLost = False

# begin loop
while True:

    # for testing dropped packets
    message, clientAddress = serverSocket.recvfrom(2048)
    splitPacket = message.split(b',')

    if int(splitPacket[0].decode()) == FULL_DATA_SYN:
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

        doneMsg = 'done'
        serverSocket.sendto(doneMsg.encode(),clientAddress)
    elif int(splitPacket[0].decode()) == SYNC_SYN:
                
        data = splitPacket[3].decode()
        splitData = data.split('!')
        data_flag = int(splitData[0])
        SegmentSize = int(splitData[1]) 

        dataAck_msg = str(DATA_ACK) + "," + str(1) + str(1) + "void"
        serverSocket.sendto(dataAck_msg.encode(), clientAddress)

    elif int(splitPacket[0].decode()) == DATA_SYN:
        #check for packet loss
        print("Checking for packet loss")
        print("SegmentSize :" + str(SegmentSize))
        packet_dropped = check_point(SegmentSize)
       
        if (packet_dropped == -1):
            HasLost = False
            check_pt = check_pt + (SegmentSize//8) 
        else:
            HasLost = True

    elif int(splitPacket[0].decode()) == CAM_FLAG:

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

    w.update()
    w.update_idletasks()
