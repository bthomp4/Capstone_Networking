from socket import *
#import signal
#import sys

# for decoding and displaying the image
import base64
from PIL import Image, ImageTk
import tkinter

from time import sleep

# starts out blank in beginning of program
picture = "test_decode.jpg"

# array to hold encoded string from client
encode_string = []

# Function Name: decode_string
# Purpose: Decodes the image from the client
def decode_string(image_64_encode):
    global encode_string
    encode_string = []
    image_64_decode = base64.decodestring(image_64_encode)
    with open(picture,'wb') as image_result:
        image_result.write(image_64_decode)
    update_image()

# Function Name: update_image
# Purpose: Updates the image being displayed in tkinter gui
def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open(picture))
    label.config(image = camImg)
    label.pack()

server_port = 12000
serverSocket = socket(AF_INET,SOCK_DGRAM)
serverSocket.bind(('',server_port))
print("The server is ready to recieve")

#discnt_client_str = 'DCNT, BYE REAR UNIT!'
#discnt_server_str = 'DCNT, Server Disconnected!'

#def signal_handler(signal,frame,clientAddress):
#	print('Ctrl+C pressed')
#	response = discnt_server_str
#	server_socket.sendto(response.encode(),clientAddress)
	
#	server_socket.close()
#	sys.exit(0)

#signal.signal(signal.SIGINT,signal_handler)

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()

while True:
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
        encode_string.append(message)

        #print(message)

        readyMsg = 'ready'

        serverSocket.sendto(readyMsg.encode(), clientAddress)
    w.update()
    w.update_idletasks()
