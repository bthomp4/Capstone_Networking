from socket import *
import argparse
import signal
import sys

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

disconnect_str = 'DCNT'

def signal_handler(signal,frame):
	print('Ctrl+C pressed')
	message = disconnect_str
	client_socket.sendto(message.encode(),(args.server_name,serverPort))
	client_socket.close()
	sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)

message = ' '

client_socket.sendto(message.encode(), (args.server_name,server_port))

