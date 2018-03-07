from socket import *

# for decoding the image
import base64
from PIL import Image

from time import sleep

# for displaying the time
#from datetime import datetime

picture = "test_decode.jpg"

def decode_string(image_64_encode):
    image_64_decode = base64.decodestring(image_64_encode)
    image_result = open(picture,'wb')
    image_result.write(image_64_decode)

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

encode_string = []

while True:
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
       
        im = Image.open(picture)

        im.show()
        sleep(2)
        im.close()

        doneMsg = 'done'
        serverSocket.sendto(doneMsg.encode(),clientAddress)
    else:
        encode_string.append(message)

        print(message)

        readyMsg = 'ready'

        serverSocket.sendto(readyMsg.encode(), clientAddress)
