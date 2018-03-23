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

# begin loop
while True:
    message, clientAddress = serverSocket.recvfrom(2048)

    # for debugging, displaying the time 
    #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    if message.decode() == 'done':
        print("if")
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

        readyMsg = 'ready'

        serverSocket.sendto(readyMsg.encode(), clientAddress)
    w.update()
    w.update_idletasks()
