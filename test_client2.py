# This program is used for testing the client program without using the PiCamera

from socket import *
import argparse

# for encoding the image 
import base64
from PIL import Image

# for displaying the time
from datetime import datetime

from time import sleep

picture = "tempPic.jpg"

DATA_SIZE = 497

def encodeImage():
    #Compress the image

    cam_pic = Image.open(picture)
    
    scaledPic = "pic_scaled.jpg"

    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save(scaledPic,quality=20) 

    image = open(scaledPic,'rb')
    image_read = image.read()
    image_64_encode = base64.encodestring(image_read)

    return image_64_encode

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

while True:
    string = encodeImage()

    encode_msgs = []

    while string:
        encode_msgs.append(string[:DATA_SIZE])
        string = string[DATA_SIZE:]

    i = 0

    # segment size
    SS = len(encode_msgs)
    newSS = str(SS)
    
    # pad segment size to be 4 bytes
    if (len(str(SS)) != 4):
        for i in range(0,len(str(SS))):
            newSS = newSS + '0'
        newSS = newSS + str(SS)
    SS = int(newSS)

    while(i < len(encode_msgs)):
        newSN = ''
        data = encode_msgs[i]

        # pad segment number to be 4 bytes
        if (len(str(i)) != 4):
            for j in range(0,len(str(i))):
                newSN = newSN + '0'
            newSN = newSN + str(i)
        SN = int(newSN)
        # DATA_CAM Flag == 5
        message = "5," + str(SS) + "," + str(SN) + "," 

        print("Sending Packet to Server")
        client_socket.sendto(message.encode() + data, (args.server_name,server_port))
        print("Recieving ready from server")
        server_message,serverAddress = client_socket.recvfrom(2048)
        i = i + 1

    print("sending done msg to server")
    message = 'done'

    client_socket.sendto(message.encode(),(args.server_name,server_port))

    print("client done, waiting for server")
    server_message,serverAddress = client_socket.recvfrom(2048)

    #print(server_message.decode())	

#client_socket.close()
