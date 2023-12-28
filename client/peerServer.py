import socket
import threading
import select


class PeerServer(threading.Thread):
    def __init__(self, username, peerServerPort):
        threading.Thread.__init__(self)
        self.username = username
        self.peerServerPort = peerServerPort
        self.tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peerServerIP = None
        self.udpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        self.peerServerIP = socket.gethostbyname(socket.gethostname())
        self.tcpServerSocket.bind((self.peerServerIP, self.peerServerPort))
        self.tcpServerSocket.listen(5)
        self.udpServerSocket.bind((self.peerServerIP, self.peerServerPort))
        self.udpServerSocket.setblocking(0)
        sockets = [self.tcpServerSocket]
        