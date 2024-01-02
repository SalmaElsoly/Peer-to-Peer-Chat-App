import threading
from socket import *
from CLI import *

# this will be the thread that will handle the peer to peer connection of one to one chat


class PeerClient(threading.Thread):
    def __init__(
        self, ipToConnect, portToConnect, username, peerServer, responseReceived
    ):
        threading.Thread.__init__(self)
        self.ipToConnect = ipToConnect
        self.username = username
        self.portToConnect = portToConnect
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.peerServer = peerServer
        self.responseReceived = responseReceived
        self.isEndingChat = False

    def run(self):
        print("Peer client started...")
        self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))
        if self.peerServer.isChatRequested == 0 and self.responseReceived is None:
            requestMessage = (
                "CHAT-REQUEST "
                + str(self.peerServer.peerServerPort)
                + " "
                + self.username
            )
            self.tcpClientSocket.send(requestMessage.encode())
            print(YELLOW+"Request message " + requestMessage + " is sent..."+RESET)
            self.responseReceived = self.tcpClientSocket.recv(1024).decode()
            print(YELLOW+"Response is " + self.responseReceived+RESET)
            self.responseReceived = self.responseReceived.split()
            if self.responseReceived[0] == "OK":
                self.peerServer.isChatRequested = 1
                self.peerServer.chattingClientName = self.responseReceived[1]
                while self.peerServer.isChatRequested == 1:
                    messageSent = input(RESET)
                    self.tcpClientSocket.send(messageSent.encode())
                    if messageSent == ":q":
                        self.peerServer.isChatRequested = 0
                        self.isEndingChat = True
                        break
                if self.peerServer.isChatRequested == 0:
                    if not self.isEndingChat:
                        try:
                            self.tcpClientSocket.send(":q ending-side".encode())
                        except BrokenPipeError as bpErr:
                            pass
                    self.responseReceived = None
                    self.tcpClientSocket.close()
            elif self.responseReceived[0] == "REJECT":
                self.peerServer.isChatRequested = 0
                print(RED+"client of requester is closing..."+RESET)
                self.tcpClientSocket.send("REJECT".encode())
                self.tcpClientSocket.close()
            elif self.responseReceived[0] == "BUSY":
                print(BLUE+"Receiver peer is busy"+RESET)
                self.tcpClientSocket.close()
        elif self.responseReceived == "OK":
            self.peerServer.isChatRequested = 1
            okMessage = "OK"
            self.tcpClientSocket.send(okMessage.encode())
            print(YELLOW+"Client with OK message is created... and sending messages"+RESET)
            while self.peerServer.isChatRequested == 1:
                messageSent = input(RESET)
                self.tcpClientSocket.send(messageSent.encode())
                if messageSent == ":q":
                    self.peerServer.isChatRequested = 0
                    self.isEndingChat = True
                    break
            if self.peerServer.isChatRequested == 0:
                if not self.isEndingChat:
                    self.tcpClientSocket.send(":q ending-side".encode())
                self.responseReceived = None
                self.tcpClientSocket.close()
