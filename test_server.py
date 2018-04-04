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
MAX_SS = 9999

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

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()

packet_count = 0
check_pt = 0
packetsRec = [0] * MAX_SS

# begin loop
while True:

    # for testing dropped packets

    message, clientAddress = serverSocket.recvfrom(2048)

    if message.decode() == 'done':
        full_string = b''
        i = 0

        while(i < len(encode_string)):
            full_string = full_string + encode_string[i]
            i = i + 1
        
        decode_string(full_string)

        doneMsg = 'done'
        serverSocket.sendto(doneMsg.encode(),clientAddress)
    else:
        packet_count = packet_count + 1
        
        # Split up packet
        splitPacket = message.split(b',')

	# First element = MSG_Flag
        MSG_Flag = int(splitPacket[0])

        # Second element = SS
        SegmentSize = int(splitPacket[1])

        # Third element = SN
        SegmentNum = int(splitPacket[2]) 
       
        packetsRec[SegmentNum] = 1

        # Append the encoded image data 
        encode_string.append(splitPacket[3])

        if (packet_count == (SegmentSize//8)):
            packet_count = 0
            packet_dropped = -1
            # loop through up to recent SN and see if there are any lost packets
            for i in range(check_pt,SegmentNum):
                if packetsRec[i] == 0:
                    packet_dropped = i
                    break
            
            # if there is a lost packet, packet_dropped will != -1
            message = str(packet_dropped)
            serverSocket.sendto(message.encode(),clientAddress) 

        check_pt = check_pt + (SegmentSize//8)
        #readyMsg = 'ready'
        
        #print("sending ready to client")
        #serverSocket.sendto(readyMsg.encode(), clientAddress)
    w.update()
    w.update_idletasks()
