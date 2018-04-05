from socket import *

# for decoding and displaying the image
import base64
from PIL import Image,ImageTk
import tkinter

from time import sleep

# for displaying the time
#from datetime import datetime

# starts out blank in beginning of program
picture = "test_decode.jpg"

# array to hold encoded string from client
encode_string = []

# Max Segment Size
MSS = 9999

# where packets need to be checked for loss
check_pt = 0

# List for storing which packets have been received
packetsRec = [0] * MSS

CAM_FLAG = 5
SYNC_SYN = 3
SYNC_ACK = 9
DATA_SYN = 10
DATA_ACK = 11
FULL_DATA_SYN = 1
FULL_DATA_ACK = 2

#Function Name: decode_string
#Usage: Decodes the image from the client
def decode_string(image_64_encode):
    global encode_string
    encode_string = []
    image_64_decode = base64.decodestring(image_64_encode)
    with open(picture,'wb') as image_result:
        image_result.write(image_64_decode)
    update_image()

def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open(picture))
    label.config(image = camImg)
    label.pack()

def check_point(SegmentSize):
    global check_pt
    global packetsRec

    print("Check_Pt: " + str(check_pt))
    packet_dropped = -1
    for i in range (check_pt,(check_pt + (SegmentSize//8))):
        if packetsRec[i] == 0:
            packet_dropped = i
            break
    packetDrop_msg = str(packet_dropped)
    serverSocket.sendto(packetDrop_msg.encode(),clientAddress)
    
    return packet_dropped

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))
print("The server is ready to recieve")

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
label.pack()

HasLost = False

# begin loop
while True:

    # for testing dropped packets
    message, clientAddress = serverSocket.recvfrom(2048)
    splitPacket = message.split(b',')

    if int(splitPacket[0].decode()) == FULL_DATA_SYN:
        print("Client done sending all packets for image")
        #reset values 
        check_pt = 0
        packetsRec = [0] * MSS        

        full_string = b''
        i = 0

        while(i < len(encode_string)):
            full_string = full_string + encode_string[i]
            i = i + 1
        
        decode_string(full_string)

        doneMsg = 'done'
        serverSocket.sendto(doneMsg.encode(),clientAddress)
    elif int(splitPacket[0].decode()) == SYNC_SYN:
                
        data = splitPacket[3].decode()
        splitData = data.split('!')
        data_flag = int(splitData[0])
        SegmentSize = int(splitData[1]) 

        dataAck_msg = str(DATA_ACK) + "," + str(1) + str(1) + "void"
        serverSocket.sendto(dataAck_msg.encode(), clientAddress)

    elif int(splitPacket[0].decode()) == DATA_SYN:
        #check for packet loss
        print("Checking for packet loss")
        print("SegmentSize :" + str(SegmentSize))
        packet_dropped = check_point(SegmentSize)
       
        if (packet_dropped == -1):
            HasLost = False
            check_pt = check_pt + (SegmentSize//8) 
        else:
            HasLost = True

        #while (packet_dropped != -1):
        #    print("Packet lost: " + str(packet_dropped)) 
        #    message,clientAddress = serverSocket.recvfrom(2048)
        #    splitPacket = message.split(b',')
        #    MSG_Flag = int(splitPacket[0])
        #    SegmentSize = int(splitPacket[1])
        #    SegmentNum = int(splitPacket[2])
        #    print("Segment Number: " + str(SegmentNum))
        #    packetsRec[SegmentNum] = 1
        #    if (SegmentNum == len(encode_string)):
        #        encode_string.append(splitPacket[3])
        #    else:
        #        encode_string[SegmentNum] = splitPacket[3]

        #    packet_dropped = check_point(SegmentSize)
        #check_pt = check_pt + (SegmentSize//8)
    elif int(splitPacket[0].decode()) == CAM_FLAG:

        # Second element = SS
        SegmentSize = int(splitPacket[1])

        # Third element = SN
        SegmentNum = int(splitPacket[2]) 
       
        packetsRec[SegmentNum] = 1

        # Append the encoded image data 
        if (SegmentNum == len(encode_string) or HasLost == False):
            encode_string.append(splitPacket[3])
        else:
            encode_string[SegmentNum] = splitPacket[3]

        print("Appending SegmentNum : " + str(SegmentNum))

        #print("Segment Num: " + str(SegmentNum))

        #if ((SegmentNum + 1) % (SegmentSize//8) == 0):
            #print("reached check point")
            #packet_dropped = -1
            # loop through up to recent SN and see if there are any lost packets
            #for i in range(check_pt,SegmentNum):
                #if packetsRec[i] == 0:
                    #packet_dropped = i
                    #break
            #print("Check_pt: " + str(check_pt))
            #print("Segment Num " + str(SegmentNum))
            #print("Value of packet_dropped " + str(packet_dropped))            
            # if there is a lost packet, packet_dropped will != -1
            #print("Sending packet_dropped message to client")
            #packetDrop_message = str(packet_dropped)
            #serverSocket.sendto(packetDrop_message.encode(),clientAddress) 

            #while (packet_dropped != -1):
                #print("while packet_dropped != -1")
                #message,clientAddress = serverSocket.recvfrom(2048)
                #splitPacket = message.split(b',')
                #MSG_Flag = int(splitPacket[0])
                #SegmentSize = int(splitPacket[1])
                #SegmentNum = int(splitPacket[2])
                #packetsRec[SegmentNum] = 1
                #print("Segment Num being stored: " + str(SegmentNum) )
                #print("Length of encode_string: " + str(len(encode_string)))
                #if (SegmentNum == len(encode_string)):
                #    encode_string.append(splitPacket[3])
                #else:
                #    encode_string[SegmentNum] = splitPacket[3] 
 
                #if ((SegmentNum + 1) % (SegmentSize//8) == 0):
                    #print("Reached check point again")
                    #packet_dropped = -1
                    #for i in range(check_pt,SegmentNum):
                    #    if packetsRec[i] == 0:
                    #        packet_dropped = i
                    #        break

                    #packetDrop_message = str(packet_dropped)
                    #serverSocket.sendto(packetDrop_message.encode(),clientAddress)
            #check_pt = check_pt + (SegmentSize//8)

        #readyMsg = 'ready'
        
        #print("sending ready to client")
        #serverSocket.sendto(readyMsg.encode(), clientAddress)
    w.update()
    w.update_idletasks()
