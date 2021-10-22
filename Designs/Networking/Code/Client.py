import os
import socket
import threading,time,random


class Client:
    def __init__(self,Address,Port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err_msg:
            print("Error Creating Socket: ", err_msg)
            sys.exit(1)

        try:
            self.sock.connect((Address, Port))
        except socket.gaierror as err_msg:
            print("Address-related error connecting to server: ", err_msg)
            sys.exit(1)

    def SendRequest(self, Request):
        try:
            self.sock.send(Request.encode())

        except socket.error as err_msg:
            print("Error while Sending Data: ", err_msg)
            sys.exit(1)

    def RecvMessage(self):
        data = self.sock.recv(1024)
        data = data.decode()
        return data

class PlayServer:
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.port = port
    
    def sendData(self, message):
        sent = self.sock.sendto(message.encode('utf-8'), (self.address, self.port))
        print(sent)

    def recvData(self):
        while True:
            data, address = self.sock.recvfrom(1024)
            data = data.decode()
            print("\nData:",data,"  From:", address)

class PSReq:
    def __init__(self):
        self.CLT = Client('localhost', 420)
        self.PSL = PlayServer('localhost', 421)
        self.Token = -1
        
    def Solo_Request(self):
        Request = "Solo|#|B1|#|S1"
        self.CLT.SendRequest(Request)
        
        #Receving Token
        self.Token = self.CLT.RecvMessage().split("|#|")[1]
        print("My Token is ",self.Token)

        if self.Token != -1:
            self.PSL.sendData(f"Ready|#|Token|#|{self.Token}")

        threading.Thread(target = self.PSL.recvData,daemon = True).start()
        event_no = 0
        time.sleep(10)
        while True:
            Event = "Player 12 Out"   
            self.sendEvent(Event, event_no)
            event_no += 1
            time.sleep(1)
            

    def sendEvent(self, Event, eno):
        self.PSL.sendData("Event |#|" + Event + "|#|Token|#|" +self.Token + "|#|" +str(eno))

if __name__ == "__main__":
    st = PSReq()
    st.Solo_Request()
