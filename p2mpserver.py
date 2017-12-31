import socket,sys
from random import *

MSS = 1056
serverPort = int(sys.argv[1])
filename = sys.argv[2]
prob = float(sys.argv[3])
#print(prob)
print('server running')
serverSeqno = 0
ackPacket = '1010101010101010'
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
serverSocket.bind(('', serverPort))
file = open(filename+'.txt', 'w')

def carry_around_add(a, b):

    c = a + b
    return (c & 0xffff) + (c >> 16)


def checksum(msg):

    # Force data into 16 bit chunks for checksum
    if (len(msg) % 2) != 0:
        msg += "0".encode('utf-8')

    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + ((msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff



data, address = serverSocket.recvfrom(MSS)
#print(data)
clientSeqno = int(data[0:32],2)
clientChecksum = int(data[32:48],2)
previous_checksum = 0
previous_seqno = 0
message = data[64:]
#print('Client sequence number and checksum:', clientSeqno, clientChecksum)
#print('ClientSeqno and ServerSeqno:',clientSeqno,serverSeqno)
if(serverSeqno == clientSeqno):
        r = random()
        if(r>prob):
                serverChecksum = checksum(message)
                #print('Server checksum:', serverChecksum)
                if(clientChecksum == serverChecksum):
                        binSegNo = '{0:032b}'.format(serverSeqno)
                        sendAck = binSegNo + '{0:016b}'.format(0) + ackPacket
                        #print('ACK: and address:',sendAck,address)
                        serverSocket.sendto(sendAck.encode('utf-8'),address)
                        file.write(message.decode('utf-8'))
                        #print('Sent ACK')
                        if(serverSeqno == 1):
                                serverSeqno = 0
                        else:
                                serverSeqno +=1
        else:
                print('Packet Loss, sequence number = ',serverSeqno)
             



while(data):
    
    data, address = serverSocket.recvfrom(MSS)
    #print(data)
    clientSeqno = int(data[0:32],2)
    clientChecksum = int(data[32:48],2)
    message = data[64:]
    #print('Client sequence number and checksum:', clientSeqno, clientChecksum)
    #print('ClientSeqno and ServerSeqno:',clientSeqno,serverSeqno)
    #print('\n\n\n\n', message)
    if(message.decode('utf-8') == ''):
        serverSocket.sendto("Last segment".encode('utf-8'),address)  
        file.write(message.decode('utf-8'))
        break
    else:
                if(serverSeqno == clientSeqno):
                        r = random()
                        if(r>prob):
                                serverChecksum = checksum(message)
                                previous_checksum = serverChecksum
                                #print('Server checksum:', serverChecksum)
                                #print('previous checksum:', previous_checksum)
                                #print('Client Checksum:', clientChecksum)
                                if(clientChecksum == serverChecksum):
                                        binSegNo = '{0:032b}'.format(serverSeqno)
                                        sendAck = binSegNo + '{0:016b}'.format(0) + ackPacket
                                        #print('ACK: and address:',sendAck,address)
                                        serverSocket.sendto(sendAck.encode('utf-8'),address)
                                        file.write(message.decode('utf-8'))
                                        #print('Sent ACK')
                                        if(serverSeqno == 1):
                                                previous_seqno = 1
                                                serverSeqno = 0
                                        else:
                                                previous_seqno = 0										
                                                serverSeqno +=1
                                else:
                                        continue
                                        
                        else:
                                print('Packet Loss, sequence number = ',serverSeqno)
                else:
                        #print('Sequence number mismatch')
                        #print('previous_checksum and clientChecksum:',previous_checksum,clientChecksum)
                        if(clientChecksum == previous_checksum):
                            binSegNo = '{0:032b}'.format(previous_seqno)
                            sendAck = binSegNo + '{0:016b}'.format(0) + ackPacket
                            serverSocket.sendto(sendAck.encode('utf-8'),address)
        
            
file.close()
print('file transfer successful')
serverSocket.close()
