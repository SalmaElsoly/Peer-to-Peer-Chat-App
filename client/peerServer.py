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
        # while sockets:
        #     readable, writable, exceptional = select.select(sockets, [], [])
        #     for sock in readable:
        #         if sock is self.tcpServerSocket:
        #             client_socket, client_address = sock.accept()
        #             client_socket.setblocking(0)
        #             sockets.append(client_socket)

    def recieve_message(self):
        try:
            data = self.udpServerSocket.recv(1024).decode().split()
            print("dataaaaaaaaaa "+str(data))
            return data
        except socket.error:
            return None
