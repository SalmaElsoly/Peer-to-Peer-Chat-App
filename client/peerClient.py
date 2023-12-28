import threading
import socket

# this will be the thread that will handle the peer to peer connection of one to one chat


class PeerClient(threading.Thread):
    def __init__(
        self, username, peerToConnectIp, peerToConnectPort, peerServer, responseReceived
    ):
        threading.Thread.__init__(self)
        self.username = username
        self.peerToConnectIp = peerToConnectIp
        self.peerToConnectPort = peerToConnectPort
        self.peerServer = peerServer
        self.responseReceived = responseReceived
        self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isInChat = False

    def run(self):
        print("Peer client started...")
        try:
            self.tcpClientSocket.connect((self.peerToConnectIp, self.peerToConnectPort))
            if self.peerServer.isChatRequested == 0 and self.responseReceived is None:
                requestMessage = (
                    "CHAT-REQUEST "
                    + str(self.peerServer.peerServerPort)
                    + " "
                    + self.username
                )
                self.tcpClientSocket.send(requestMessage.encode())
                print("Request message " + requestMessage + " is sent...")
                self.responseReceived = self.tcpClientSocket.recv(1024).decode()
                print("Response message " + self.responseReceived + " is received...")
                self.responseReceived = self.responseReceived.split()
                if self.responseReceived[0] == "CHAT-ACCEPTED":
                    self.peerServer.isChatRequested = 1
                    self.peerServer.connectedPeerSocket = self.tcpClientSocket
                    self.peerServer.connectedPeerIP = self.peerToConnectIp
                    self.peerServer.connectedPeerPort = self.peerToConnectPort
                    self.peerServer.chattingClientName = self.responseReceived[1]
                    self.isInChat = True
                    print("Chat is accepted...")
                else:
                    self.tcpClientSocket.close()
                    print("Chat is not accepted...")
        except socket.error:
            print("Peer is not online...")
            self.tcpClientSocket.close()
