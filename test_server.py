from socket import *

# for decoding and displaying the image
import base64
from PIL import Image,ImageTk
import tkinter

from time import sleep

#for displaying the time
#from datetime import datetime

#starts out blank in beginning of program
picture = "test_decode.jpg"

# array to hold encoded string from client
encode_string = []

# array to store packets lost
lost_packets = []

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
    print("Updated")

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
print("Loaded")
label.pack()

packet_count = 0

# begin loop
while True:
    # for testing dropped packets

    message, clientAddress = serverSocket.recvfrom(2048)

    if message.decode() == 'done':

        print("ready to assemble")
        
        # reset packet count back to zero
        packet_count = 0

        full_string = b''
        i = 0

        while(i < len(encode_string)):
            full_string = full_string + encode_string[i]
            i = i + 1

        print(full_string)
        decode_string(full_string)

        doneMsg = 'done'
        print(doneMsg)
        serverSocket.sendto(doneMsg.encode(),clientAddress)
    else:
        packet_count = packet_count + 1;

        print("recieved new packet from client")
        newPacket = message.decode()

        # Split up packet
        splitPacket = newPacket.split(",")
        
        print(splitPacket[3].encode())
        encode_string.append(splitPacket[3].encode())
        
        readyMsg = 'ready'
        
        print("sending ready to client")
        serverSocket.sendto(readyMsg.encode(), clientAddress)
    w.update()
    w.update_idletasks()
