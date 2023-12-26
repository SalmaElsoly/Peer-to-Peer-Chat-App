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

    def run(self):
        self.peerServerIP = socket.gethostbyname(socket.gethostname())
        self.tcpServerSocket.bind((self.peerServerIP, self.peerServerPort))
        self.tcpServerSocket.listen(5)

        sockets = [self.tcpServerSocket]
        while sockets:
            readable, writable, exceptional = select.select(sockets, [], [])
            for sock in readable:
                if sock is self.tcpServerSocket:
                    client_socket, client_address = sock.accept()
                    client_socket.setblocking(0)
                    sockets.append(client_socket)
