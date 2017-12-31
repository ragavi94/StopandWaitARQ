import socket
import sys,os
import threading
from threading import Thread
import datetime
BUFFER_SIZE = 1
HEADER_SIZE = 8
arg_size = len(sys.argv)
#print(arg_size)
server_port = int(sys.argv[arg_size-3])
MSS = int(sys.argv[arg_size-1]) - HEADER_SIZE
server_ip = []
#server_ip = ['localhost','192.168.217.151']
c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
filename = sys.argv[arg_size-2]
loc = os.path.dirname(sys.argv[0])
dataPacket = '0101010101010101'
sendData = ''
for i in range(1,arg_size-3):
	server_ip.append(sys.argv[i])
print(server_ip)

def rdt_send(offset):
        #print('inside rdt_send')
        f=open(loc+'\\'+filename+'.txt','rb')
        f.seek(offset)
        l=f.read(BUFFER_SIZE)	
        #print('l',l)
        if(l):
                return l
        else:
                return b''
        f.close()
                
def carry_around_add(a, b):
    
    c = a + b
    return (c & 0xffff) + (c >> 16)


def checksum(msg):
    #print('In checksum function:', msg)

    if (len(msg) % 2) != 0:
        msg += "0".encode('utf-8')

    s = 0
    for i in range(0, len(msg), 2):
        #print('Message:', msg[i],msg[i+1])
        w = msg[i] + ((msg[i+1]) << 8)
        #print('Message:', msg[i],msg[i+1])
        s = carry_around_add(s, w)
    return ~s & 0xffff
        
                

class peerThread(threading.Thread):
        def __init__(self,data,server_addr):
                threading.Thread.__init__(self)
                self.lock=threading.Lock()
                self.server_addr = server_addr
                self.data = data
        def run(self):
                #print('new thread started for a new server')
                #print('In send thread, data to be sent is:', self.data)
                #flag = False
                #while not flag:
                #print('sending data')
                #print(self.server_addr)
                c_sock.sendto(self.data,self.server_addr)
                            
                        
threads=[]



file_size = os.stat(loc+'\\'+filename+'.txt').st_size
#print('filesize:',file_size)
remaining_size = file_size
offset = 0
count = 0

#ackList = server_ip
segment_no = 0
#print('sending file')
startTime = datetime.datetime.now()
while(remaining_size>=0):
        ackList = list(server_ip)
        ackCount = 0
        local_buffer=b''
        print('Remaining size:',remaining_size)
        #print(file_size,remaining_size)
        while(len(local_buffer)<=MSS):
                #print('offset:',offset)
                #print('i:',i)
                tmp=rdt_send(offset)
                if((len(tmp)==1) and (len(local_buffer)<MSS)):
                        local_buffer=local_buffer.__add__(tmp)
                        #print(local_buffer)
                elif((len(tmp)<1) and (len(local_buffer)<MSS)):
                        local_buffer.__add__(tmp)
                        binSegNo = '{0:032b}'.format(segment_no)
                        #print('Length of binary seq no:', len(binSegNo))
                        check = checksum(local_buffer)
                        binaryCheck = '{0:016b}'.format(check)
                        #print('Length of binary checksum:', len(binaryCheck))
                        #print('Length of data Packet:', len(dataPacket))
                        #print('Length of local buffer',len(local_buffer))
                        sendData = binSegNo.encode('utf-8') + binaryCheck.encode('utf-8') + dataPacket.encode('utf-8') + local_buffer
                        #print('Size of sendData:', len(sendData))
                        #print('printing data to be sent: ',local_buffer)
                        #print('sending segment ',segment_no)
                        count+=1
                        #print('Count:', count)
                        for ip_addr in server_ip:
                                server_addr = (ip_addr, server_port)
                                #print(server_addr)
                                new_peer=peerThread(sendData,server_addr)
                                new_peer.start()
                                threads.append(new_peer)
                        for t in threads:
                            t.join()
                                #new_peer.join()
                                #if(segment_no == 1):
                                        #segment_no = 0
                                #else:
                                        #segment_no+=1
                        while(ackCount!=len(server_ip)):
                            c_sock.settimeout(1)
                            try:
                                #print('Waiting for ACK from:',self.server_addr[0])
                                ack,address = c_sock.recvfrom(MSS)
                                serverSeqno = int(ack[0:32],2)
                                if(serverSeqno == segment_no):
                                    #print('ACK LIST IN TRY BLOCK BEFORE REMOVING:', ackList)
                                    #print('trying to remove:',address[0])
                                    if(address[0] in ackList):
                                        ackCount+=1
                                        ackList.remove(address[0])
								#print('address to be removed:',address[0])
                                #print('Before removal:',ackList)
                                
                                #print('ACK LIST IN TRY BLOCK, after removal:', ackList)
                                #print('ACK from: ',ack, address[0])
                            except socket.timeout:
                                #print('Timeout, Sequence number = ', segment_no)
                                #print('ACK LIST:', ackList)
                                for ip_addr in ackList:
                                    server_addr = (ip_addr, server_port)
                                    #print(server_addr)
                                    new_peer=peerThread(sendData,server_addr)
                                    new_peer.start()
                                    threads.append(new_peer)
                                for t in threads:
                                    t.join()
                                continue
                                        
                        str=''
                        binSegNo = '{0:032b}'.format(segment_no)
                        #check = checksum(local_buffer)
                        binaryCheck = '{0:016b}'.format(0)
                        sendData = binSegNo.encode('utf-8') + binaryCheck.encode('utf-8') + dataPacket.encode('utf-8') + str.encode('utf-8')
                        for ip_addr in server_ip:
                                server_addr = (ip_addr, server_port)
                                #print(server_addr)
                                new_peer=peerThread(sendData,server_addr)
                                new_peer.start()
                                threads.append(new_peer)
                        for t in threads:
                            t.join()
                                #new_peer.join()
                        break
                else:
                    break
                
                offset = offset + BUFFER_SIZE
                if((len(tmp)==1) and (len(local_buffer)==MSS)):
                        #print('Length of segment number:', len(segment_no))
                        binSegNo = '{0:032b}'.format(segment_no)
                        check = checksum(local_buffer)
                        binaryCheck = '{0:016b}'.format(check)
                        #print('Length of binary seq no:', len(binSegNo))
                        #print('Length of binary checksum:', len(binaryCheck))
                        #print('Length of data Packet:', len(dataPacket))
                        #print('Length of local buffer',len(local_buffer))
                        sendData = binSegNo.encode('utf-8') + binaryCheck.encode('utf-8') + dataPacket.encode('utf-8') + local_buffer
                        #print('Length of sendData:', len(sendData))
                        count+=1
                        #print('Count:', count)
                        #print('printing data to be sent: ',local_buffer)
                        #print('sending segment ',segment_no)
                        for ip_addr in server_ip:
                                server_addr = (ip_addr, server_port)
                                #print(server_addr)
                                new_peer=peerThread(sendData,server_addr)
                                new_peer.start()
                                threads.append(new_peer)
                        #print(threads)
                        for t in threads:
                            t.join()
						
                        while(ackCount!=len(server_ip)):
                            c_sock.settimeout(0.05)
                            try:
                                #print('Waiting for ACK from:',server_addr[0])
                                ack,address = c_sock.recvfrom(MSS)
                                #print('ACK:',ack,address)
                                serverSeqno = int(ack[0:32],2)
                                if(serverSeqno == segment_no):
                                    
                                    #print('ACK LIST IN TRY BLOCK BEFORE REMOVING:', ackList)
                                    #print('trying to remove:',address[0])
                                    if(address[0] in ackList):
                                        ackList.remove(address[0])
                                        ackCount+=1
                                    #print('ACK LIST IN TRY BLOCK:', ackList)
                                    #print('ACK from: ',ack, address[0])
                            except socket.timeout:
                                #print('Timeout, Sequence number = ', segment_no)
                                #print('ACK LIST:', ackList)
                                for ip_addr in ackList:
                                    server_addr = (ip_addr, server_port)
                                    #print(server_addr)
                                    new_peer=peerThread(sendData,server_addr)
                                    new_peer.start()
                                    threads.append(new_peer)
                                for t in threads:
                                    t.join()
                                continue
							
                                
                                
        if(segment_no == 1):
                segment_no = 0
                #print('Segment number after incrementing: 1 to 0')
        else:
                segment_no += 1
                #print('Segment number after incrementing: 0 to 1')                
        remaining_size = remaining_size - MSS
                

endTime = datetime.datetime.now()
print('Time taken to transmit the file:', (endTime-startTime))