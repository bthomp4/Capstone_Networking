# This program is used for the testing the client side with the PiCamera

from socket import *
import argparse

# for encoding the image 
import base64
from PIL import Image

# for displaying the time
from datetime import datetime

from picamera import PiCamera

DATA_SIZE = 497
picture = 'test.jpg'

camera = PiCamera()

def encodeImage():
    #Compress the image
    cam_pic = Image.open(picture)
    
    print(cam_pic.size)
    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save("test2_scaled.jpg",quality=20) 

    image = open('test2_scaled.jpg','rb')
    image_read = image.read()
    image_64_encode = base64.encodestring(image_read)

    return image_64_encode

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

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

        # for debugging, displaying time
        #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        print("sending picture data")
        client_socket.sendto(message, (args.server_name,server_port))
        server_message,serverAddress = client_socket.recvfrom(2048)
        print("recieved server message")
        i = i + 1

    print("sending done msg to server")
    message = 'done'
    client_socket.sendto(message.encode(),(args.server_name,server_port))

    print("client done, waiting for server")
    server_message,serverAddress = client_socket.recvfrom(2048)

#client_socket.close()
