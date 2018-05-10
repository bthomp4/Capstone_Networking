# This program is used for the testing the client side with just PiCamera

from socket import *
import argparse

import signal
import sys

from time import *

# -------------------
# Defining Functions
# -------------------

# ---------------
# Main Script
# ---------------

# Set variables
DATA_SIZE   = 1500
VOID_DATA   = "VOID"
SS_FlagSize = 4
SN_FlagSize = 4
DCNT_flag   = 0

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

def signal_handler(signal,frame):
    client_socket.close()
    print("full: " + str(sum(times)/len(times)))
    print("loop: " + str(sum(loop)/len(loop)))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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

    msg = "0" * 1500
    
    # segment size
    SS = str(len(msg))

    lstart = time()
    client_socket.sendto(msg.encode(), (args.server_name,server_port))

    # recieving message from server
    response,serverAddress = client_socket.recvfrom(2048)
    lstop = time()
    loop.append(lstop - lstart)
    
    stop = time()
    print("end process")
    times.append(stop - start)
