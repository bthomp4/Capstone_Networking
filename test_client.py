
from socket import *
import argparse
#import signal
import sys

# for encoding the image #
import base64
from PIL import Image

def encodeImage():
    image = open('dog1.jpg','rb')
    image_read = image.read()
    image_64_encode = base64.encodestring(image_read)

    return image_64_encode

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

#disconnect_str = 'DCNT'

#def signal_handler(signal,frame):
#       print('Ctrl+C pressed')
#       message = disconnect_str
#       client_socket.sendto(message.encode(),(args.server_name,serverPort))
#       client_socket.close()
"client.py" 58L, 1340C                              21,1          Top

