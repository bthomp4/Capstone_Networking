from socket import *

# for decoding the image
import base64
from PIL import Image

#for displaying the image
import tkinter
from PIL import Image, ImageTk

from time import sleep

#for displaying the time
#from datetime import datetime

#starts out blank in beginning of program
picture = "test_decode.jpg"

#Function Name: decode_string
#Usage: Decodes the image from the client
def decode_string(image_64_encode):
    image_64_decode = base64.decodestring(image_64_encode)
    image_result = open(picture,'wb')
    image_result.write(image_64_decode)

def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open(picture))
    label.config(image = camImg)
    label.after(1000,update_image)
    print("Updated")

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

# array to hold encoded string from client
encode_string = []

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
print("Loaded")
label.pack()

# begin loop
message, clientAddress = serverSocket.recvfrom(2048)

# for debugging, displaying the time 
#print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

if message.decode() == 'done':
    full_string = b''
    i = 0

    while(i < len(encode_string)):
        full_string = full_string + encode_string[i]
        i = i + 1

    decode_string(full_string)

    #update the image after its been decoded
    update_image() 
    doneMsg = 'done'
    serverSocket.sendto(doneMsg.encode(),clientAddress)
else:
    encode_string.append(message)

    print(message)

    readyMsg = 'ready'

    serverSocket.sendto(readyMsg.encode(), clientAddress)
w.mainloop()
