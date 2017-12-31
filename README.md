# StopandWaitARQ
Implementation of the Point-2-Multi point reliable data transfer protocol using Stop and Wait ARQ model
There are two files p2mpclient.py and p2mpserver.py. These are the client and server files.
To run the server, the program is invoked as follows using the command line,

p2mpserver.py 7735 <fileName> <loss-probability>

Example: p2mpserver.py 7735 recv_file 0.05

To run the client , the program is invoked as follows using the command line,

p2mpclient.py <server1 ipaddress> <server2 ipaddress> .. <server n address> 7735 <fileName> MSS

Example: p2mpclient.py 192.168.1.2 192.168.1.12 7735 one_mb_test 500
