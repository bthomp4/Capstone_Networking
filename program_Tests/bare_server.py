from socket import *

from time import *

import signal
import sys

# ------------------
# Defining Functions
# ------------------

# ---------------
# Main Script
# ---------------

# Set variables
VOID_DATA = "VOID"

# Max Segment Size
MSS   = 9999
MSS_1 = "0001"
SN_1  = "0001"

# where packets need to be checked for loss
check_pt = 0

# List for storing which packets have been received
packetsRec = [0] * MSS

# Setting up socket
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

def signal_handler(signal,frame):
    serverSocket.close()
    print("full: " + str(sum(times)/len(times)))
    print("loop: " + str(sum(loop)/len(loop)))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# begin loop
lost = 0

start = 0
stop = 0
times = []
flag = False
lstart = 0
lstop = 0
loop = []
while True:

    print("start process")
    start = time()
    # for testing dropped packets
    response, clientAddress = serverSocket.recvfrom(2048)
    print("recieved number of messages")

    message = "hi"
    serverSocket.sendto(message.encode(),clientAddress)
    loop.append(lstop - lstart)
    
    stop = time()
    print("end process")
    times.append(stop - start)
