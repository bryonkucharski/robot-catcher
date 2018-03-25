#!/usr/bin/env python 

""" 
Bryon Kucharski
Wentworth Institute of Technology
Spring 2018

TCP/IP server to send/receive data from a socket
""" 

import socket 

class tcp_socket:

    def __init__(self, host,port,backlog,size):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.size = size
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.s.bind((self.host,self.port)) 
        self.s.listen(self.backlog)

        print("Waiting for Client to Connect")
        self.client, self.address = self.s.accept() 
        print("Client connected.")
        self.sendData("TCP connection with Python established")

    def getData(self):
        data = self.client.recv(self.size).decode().rstrip()
        return data
    
    def sendData(self, msg):
        self.client.send((msg + "\n").encode())

'''    
server = tcp_socket(
                    host = '',
                    port = 50000, 
                    backlog = 5, #amount of requests to queue at one time
                    size = 1024 
                    )
   
data = server.getData()
print(data)
  
'''

      
        

