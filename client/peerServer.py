import socket
import threading
import select
import logging

class PeerServer(threading.Thread):
    def __init__(self, username, peerServerPort):
        threading.Thread.__init__(self)
        self.username = username
        self.tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peerServerPort = peerServerPort
        self.isChatRequested = 0
        self.connectedPeerSocket = None
        self.connectedPeerIP = None
        self.connectedPeerPort = None
        self.isOnline = True
        self.chattingClientName = None

    def run(self):
        print("Peer server started...")
        self.tcpServerSocket.bind(("", self.peerServerPort))
        self.tcpServerSocket.listen(1)
        inputs = [self.tcpServerSocket]
        while inputs and self.isOnline:
            try:
                readable, writable, exceptional = select.select(
                    inputs, [], inputs
                )
                for sock in readable:
                    if sock is self.tcpServerSocket:
                        clientSocket, clientAddress = self.tcpServerSocket.accept()
                        clientSocket.setblocking(0)
                        inputs.append(clientSocket)
                        print("Peer client is connected...")
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))
                    