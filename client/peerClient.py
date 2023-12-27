import threading
import socket


class PeerClient(threading.Thread):
    def __init__(self,username, chatRoomUsers):
        threading.Thread.__init__(self)
        self.running = True
        self.username = username
        self.chatRoomUsers = chatRoomUsers
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        print("PeerClient thread started")
    def send_message(
        self,
        message,
    ):
        message = "MESSAGE "+self.username + ": " + message
        for user in self.chatRoomUsers:
            dest_ip = user[1]
            dest_port = int(user[2])
            self.udpSocket.sendto(message.encode(), (dest_ip, dest_port))

    def stop(self):
        self.running = False
        self.udpSocket.close()
