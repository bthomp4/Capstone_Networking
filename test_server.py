
m socket import *

import base64
from PIL import Image

def decode_string(image_64_encode):
    print("hello")
    image_64_decode = base64.decodestring(image_64_encode)
    image_result = open('dog1_decode.jpg','wb')
    image_result.write(image_64_decode)

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

encode_string = []

while True:
    message, clientAddress = serverSocket.recvfrom(2048)

    if message.decode() == 'done':
        print("In if")

        full_string = b''
        i = 0

        while(i < len(encode_string)):
            full_string = full_string + encode_string[i]
            i = i + 1

        decode_string(full_string)

"server.py" 44L, 1020C                              1,1           Top

