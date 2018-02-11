from socket import *

server_port = 12000
server_socket = socket(AF_INET,SOCK_DGRAM)
server_socket.bind(('',server_port))

discnt_client_str = 'DCNT,Bye Client!'
discnt_server_str = 'DCNT,Server Disconnected!'

def signal_handler(signal,frame,clientAddress):
	print('Ctrl+C pressed')
	response = discnt_server_str
	server_socket.sendto(response.encode(),clientAddress)
	
	server_socket.close()
	sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)

while True:
	message, clientAddress = server_socket.recvfrom(2048)
	
	dec_msg = message.decode().split(',')
	
	''' debug print message id '''
	print(dec_msg[0])
	
	
