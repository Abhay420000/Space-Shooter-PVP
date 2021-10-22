import os
import socket
import threading
import socketserver
import time
import random

#from main import Bullets


class ServerForever:
    def __init__(self,Address,Port,n):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #setting re-use ablity
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((Address, Port))

        self.sock.listen(n)
        

    def AcceptCON(self):
        while True:
            client, Address = self.sock.accept()
            threading.Thread(target = self.TrackCT, args = (client, Address), daemon = True).start()
    
    def TrackCT(self, client, Address):
        Client_Request = ""
        while True:
            try:
                Client_Request = client.recv(100)
                print(1)
                print(Client_Request)
                Client_Request = Client_Request.decode()

                if self.IsValid(Client_Request):
                    self.ProcessRequest(Client_Request, client, Address)
                else:
                    client.send(b"Invalid Request")

            except ConnectionResetError as err:
                print("Error:",err)
                break
            #time.sleep(1)

    def IsValid(self, Request):
        """
            Checks Weather Request Receved is valid or not.
            If Valid => Return True
            Else => Return False
        """
        return True

    def ProcessRequest(self, Request, client, Address):
        #Mode|#Bullet|#|Ship|#|
        print("Processing Request")
        RL = Request.split("|#|")
        if RL[0] == "Solo":
            Ship = RL[1]
            Bullet = RL[2]
            global solo_list
            Token = random.randint(1,10000)
            solo_list.append([Ship, Bullet, Address, Token])
            client.send(b"Starting_Game|#|"+str(Token).encode())
        while True:
            time.sleep(1)
        print("Request had been Processed.")
        


class PServer:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
        self.sock.bind((host, port))
        
        self.Data = ""
        threading.Thread(target = self.RecvData, daemon = True).start()
    
    def RecvData(self):
        while True:
            data, address = self.sock.recvfrom(1024)
            self.Data = self.Data + "@$@" + data.decode() + "|--|" + str(address) + "@$@"

    def SendData(self, data, address):
        data = data.encode()
        sent = self.sock.sendto(data, address)
    
    def make_batches(self):
        global solo_list
        while True:
            plist = []
            if len(solo_list) >= 2:
                plist.append(solo_list[0])
                plist.append(solo_list[1])
                solo_list = solo_list[2::]
                threading.Thread(target= self.MakeMapForSolo, args = (plist,), daemon= True).start()
            else:
                time.sleep(1)
                #print("Waiting For Players!!!")

    def MatchAddress(self,Plist):
        add_list = []
        
        #self.Data = @$@Ready|#|Token|#|6862|--|('127.0.0.1', 50672)@$@@$@Ready|#|Token|#|8402|--|('127.0.0.1', 50673)@$@
        #print("self.Data = ",self.Data)
        #print("Plist = ",Plist)

        rd = []
        
        for i in range(len(Plist)):
            TK_in_Server = Plist[i][3]
            dlist = self.Data.split("@$@")
            for Players_Data in dlist:
                if Players_Data != "":
                    rd.append(Players_Data)
                    Data_Add = Players_Data.split("|--|")
                    #print(Data_Add)
                    if "Ready|#|Token|#|" in Data_Add[0]:
                        RD = Data_Add[0].split("|#|")
                        TK = RD[2]

                        if int(TK) == TK_in_Server:
                            add_list.append((TK, eval(Data_Add[1])))
        for i in rd:
            self.Data = self.Data.replace(i,"")
        print(self.Data)
        return add_list
    
    def MakeMapForSolo(self,plist):
        #plist = [[Ship,Bullet,Address,Token], [Ship,Bullet,Address,Token]]

        #Getting Players Address
        print("Plist:",plist)
        address_list = self.MatchAddress(plist)
        
        event_list = []

        print("\nAddress_list: ",address_list)
        
        #Setting Player Initial Positions
        player_pos_list = [[10,2], [10,8]]
        for i in range(len(player_pos_list)):
            self.SendData(f"Self_Pos_Initial:{player_pos_list[i]}", address_list[i][1])
        

        #Sending Opponenent Initial Position
        for i in range(len(plist)):
            Assets_Data = plist[i]
            for j in range(len(plist)):
                if plist[j] != Assets_Data:
                    self.SendData(f"Ship:{plist[i][0]}|#|Bullet:{plist[i][1]}|#|Opponent-Token:{plist[i][3]}",address_list[j][1])

        #Starting Game
        for i in range(1,4):
            for j in address_list:
                self.SendData(f"Starting in {str(4-i)}", j[1])
            time.sleep(1)

        while True:
            data_list = self.Data.split("@$@")
            print(data_list)
            for i in data_list:
                if (i != "") and ("Event" in i):
                    k = i.split("|#|")
                    
                    for j in address_list:
                        if k[3] != j[0]:
                            self.SendData(i,j[1])
                            event_list.append(i)

                    self.Data = self.Data.replace(i, "")
            time.sleep(0.01)


solo_list = []


if __name__ == "__main__":
    SRV = ServerForever('localhost', 420, 10)
    PSR = PServer('localhost',421)
    threading.Thread(target = (PSR.make_batches),).start()
    SRV.AcceptCON()
