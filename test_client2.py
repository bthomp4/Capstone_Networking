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
scaledPic = "pic_scaled.jpg"

DATA_SIZE = 500
SS_FlagSize = 4
SN_FlagSize = 4

def encodeImage():
    #Compress the image
    cam_pic = Image.open(picture)

    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save(scaledPic,quality=20) 

    with open(scaledPic,'rb') as image:
        image_64_encode = base64.encodestring(image.read())

    print(image_64_encode)

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

    num_packet = 0

    # segment size
    SS = str(len(encode_msgs))
    
    # pad segment size to be 4 bytes
    if (len(SS) != SS_FlagSize):
        for i in range(0,(SS_FlagSize - len(SS))):
            SS = '0' + SS

    while(num_packet < len(encode_msgs)):
        data = encode_msgs[num_packet]

        # Segment Number
        SN = str(num_packet)

        # pad segment number to be 4 bytes
        if (len(SN) != SN_FlagSize):
            for l in range(0,(SN_FlagSize + len(SN))):
                SN = '0' + SN

        # DATA_CAM Flag == 5
        packetInfo = '5,' + SS + ',' + 'str(SN)' + ',' 

        print(packetInfo.encode() + data)

        print("Sending Packet to Server")
        client_socket.sendto(packetInfo.encode() + data, (args.server_name,server_port))
        #client_socket.sendto(data,(args.server_name,server_port))
        print("Recieving ready from server")
        server_message,serverAddress = client_socket.recvfrom(2048)
        i = i + 1

    print("sending done msg to server")
    message = 'done'

    client_socket.sendto(message.encode(),(args.server_name,server_port))

    print("client done, waiting for server")
    server_message,serverAddress = client_socket.recvfrom(2048)

client_socket.close()
