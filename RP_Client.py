# This program will be the final version for the Client program

from socket import *
import argparse
#import signal
#import sys

# for encoding the image
import base64
from PIL import Image

from picamera import PiCamera

DATA_SIZE = 497
picture = "cameraPic.jpg"
scaledPic = "cameraPic_scaled.jpg"

camera = PiCamera()

def encodeImage():
    # Compress the image
    cam_pic = Image.open(picture)

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

#disconnect_str = 'DCNT'
#ssd_str = 'SSD'
#rcd_str = 'RCD'

#def signal_handler(signal,frame):
#	print('Ctrl+C pressed')
#	message = disconnect_str
#	client_socket.sendto(message.encode(),(args.server_name,serverPort))
#	client_socket.close()
#	sys.exit(0)

#signal.signal(signal.SIGINT,signal_handler)

while True:
    camera.capture(picture)

    string = encodeImage()

    encode_msgs = []

    while string:
        encode_msgs.append(string[:DATA_SIZE])
        string = string[DATA_SIZE:]

    i = 0

    while(i < len(encode_msgs)):
        message = encode_msgs[i]

        client_socket.sendto(message, (args.server_name,server_port))
        server_message,serverAddress = client_socket.recvfrom(2048)
        i = i + 1

    message = 'done'
    client_socket.sendto(message.encode(),(args.server_name,server_port))

    server_message,serverAddress = client_socket.recvfrom(2048)

client_socket.close()
