from socket import *
import signal
import sys

#for decoding the image
import base64
from PIL import Image

#for displaying the time
from datetime import datetime

def decode_string(image_64_encode):
    image_64_decode = base64.decodestring(image_64_encode)
    image_result = open('test2_decode.jpg','wb')
    image_result.write(image_64_decode)

server_port = 12000
serverSocket = socket(AF_INET,SOCK_DGRAM)
serverSocket.bind(('',server_port))
print("The server is ready to recieve")

encode_string = []

#discnt_client_str = 'DCNT, BYE REAR UNIT!'
#discnt_server_str = 'DCNT, Server Disconnected!'

#def signal_handler(signal,frame,clientAddress):
#	print('Ctrl+C pressed')
#	response = discnt_server_str
#	server_socket.sendto(response.encode(),clientAddress)
	
#	server_socket.close()
#	sys.exit(0)

#signal.signal(signal.SIGINT,signal_handler)

while True:
    message, clientAddress = serverSocket.recvfrom(2048)

    # for debugging, displaying the time
    print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

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

        print(message)

        readyMsg = 'ready'

        serverSocket.sendto(readyMsg.encode(), clientAddress)
