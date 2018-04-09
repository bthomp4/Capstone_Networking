# This program is used for testing the client program without using the PiCamera

from socket import *
import argparse

# for encoding the image 
import base64
from PIL import Image

# for displaying the time
from datetime import datetime

from time import sleep

picture = "tempPic.jpg"
scaledPic = "pic_scaled.jpg"

DATA_SIZE = 500
SS_FlagSize = 4
SN_FlagSize = 4

# for testing dropped packets
drop_packets = [0,1,2,3,4,5,6,7]
#drop_packets = []

def encodeImage():
    # Compress the image
    cam_pic = Image.open(picture)

    cam_pic = cam_pic.resize((800,480),Image.ANTIALIAS)
    cam_pic.save(scaledPic,quality=20) 

    with open(scaledPic,'rb') as image:
        image_64_encode = base64.encodestring(image.read())

    print(image_64_encode)

    return image_64_encode

server_port = 12000
client_socket = socket(AF_INET,SOCK_DGRAM)

parser = argparse.ArgumentParser(description='sending images')
parser.add_argument('-s', dest='server_name', help='specifies the IP of the server, this is required', required=True)
args = parser.parse_args()

while True:
    string = encodeImage()

    encode_msgs = []

    while string:
        encode_msgs.append(string[:DATA_SIZE])
        string = string[DATA_SIZE:]

    num_packet = 0

    # segment size
    SS = str(len(encode_msgs))
    
    # pad segment size to be 4 bytes
    if (len(SS) != SS_FlagSize):
        for i in range(0,(SS_FlagSize - len(SS))):
            SS = '0' + SS
     
    check_point = (int(SS)//8)
    print("Check_point value" + str(check_point))
    packet_count = 0

    #Sending Sync_Syn == 3
    syncSyn_data = "5!" + SS
    message = "3," + str(1) + ',' + str(1) + ',' + syncSyn_data

    client_socket.sendto(message.encode(), (args.server_name,server_port))

    #Waiting for Sync_Ack == 9
    server_message,serverAddress = client_socket.recvfrom(2048)

    while(num_packet < len(encode_msgs)):		
        
        packet_count = packet_count + 1
        print("Segment Number (starting at 0) " + str(num_packet))
        # remove later --------
        if num_packet not in drop_packets:
        # remove later --------
            data = encode_msgs[num_packet]

            # Segment Number
            SN = str(num_packet)

            # pad segment number to be 4 bytes
            if (len(SN) != SN_FlagSize):
                for l in range(0,(SN_FlagSize - len(SN))):
                    SN = '0' + SN

            # DATA_CAM Flag == 5
            packetInfo = '5,' + SS + ',' + SN + ',' 

            print("Sending Packet to Server")
            client_socket.sendto(packetInfo.encode() + data, (args.server_name,server_port))
            
        # if sent 1/8 of SS
        print("Packet_count: " + str(packet_count))
        if (packet_count == check_point):		
            print("Packet_count == check_point")
            
            # reset the packet count
            packet_count = 0 
                
            # sending data syn == 10 to server
            print("Sending Data Syn to Server")
            dataSyn_msg = "10,1,1,void"
            client_socket.sendto(dataSyn_msg.encode(), (args.server_name,server_port))
            # waiting to see if all packets have been recieved
            print("Waiting for server to send ACK message")
            server_message,serverAddress = client_socket.recvfrom(2048)

            packet_lost = int(server_message.decode())
            print("Printing value of packet_lost " + str(packet_lost))

            while (packet_lost != -1):
                print("OH NO, WE LOST A PACKET!!!!")
                print("Packet_Lost: " + str(packet_lost))
                for num_msg in range(packet_lost,(num_packet+ 1)):
                    print("Segment Num being sent: " + str(num_msg))
                    data = encode_msgs[num_msg]
                    SN = str(num_msg)
                    if (len(SN) != SN_FlagSize):
                        for l in range(0,(SN_FlagSize + len(SN))):
                            SN = '0' + SN
                    packetInfo = '5,' + SS + ',' + SN + ','
                    print("Sending Packet to Server")
                    client_socket.sendto(packetInfo.encode() + data, (args.server_name, server_port))
                     
                # sending data syn to server
                print("Sending Data Syn to Server")
                dataSyn_msg = "10,1,1,void"
                client_socket.sendto(dataSyn_msg.encode(), (args.server_name,server_port))

                print("Waiting for server to send ACK message")
                server_message,serverAddress = client_socket.recvfrom(2048)


                packet_lost = int(server_message.decode())                
                
        num_packet = num_packet + 1

    print("sending done msg to server")
    dataSyn_message = "1,1,1,void"

    client_socket.sendto(dataSyn_message.encode(),(args.server_name,server_port))

    print("client done, waiting for server")
    dataAck_message,serverAddress = client_socket.recvfrom(2048)

client_socket.close()
