import select
import socket
import threading
import time
import tabulate
from CLI import *


import peerServer as PS
import peerClient as PC





SERVER_TCP_PORT = 5050
SERVER_UDP_PORT = 1515


class Peer:
    def __init__(self):
        self.serverIP = input("Enter Server IP: ")
        self.serverPort = SERVER_TCP_PORT
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.connect((self.serverIP, self.serverPort))
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind((socket.gethostbyname(socket.gethostname()), 0))
        self.peerServerPort = None
        self.peerServer = None
        self.peerClient = None
        self.username = None
        self.helloMessageRunFlag = None
        self.chatRoomMessageReceiveFlag = False
        self.chatRoomUsers = None
        option = 0
        while option != "9":
            print(
                MAGENTA
                + """ Choose one of the following options:
            1. Login
            2. Create Account
            3. List Online Users
            4. Start One to One Chat
            5. List Chat Rooms
            6. Create Chat Room
            7. Join Chat Room
            8. Logout
            9. Exit""" + RESET
            )
            option = input(GREEN + "Enter your option: " + RESET)
            if option == "1":
                username = input(GREEN + "Enter username: "+ RESET)
                password = get_password()
                peerServerPort = input(GREEN + "Enter your port number: "+ RESET)
                self.login(username, password, peerServerPort)
            elif option == "2":
                username = input(GREEN + "Enter username: "+ RESET)
                password = get_password()
                while not validate_password(password):
                    print(
                        RED
                        + "Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character"+RESET
                    )
                    password = get_password()
                self.createAccount(username, password)
            elif option == "3":
                if self.username != None:
                    self.listOnlineUsers()
                else:
                    print(RED + "Please Login/Signup first!"+RESET)
            elif option == "4":
                if self.username != None:
                    self.startOneToOneChat()
                else:
                    print(RED + "Please Login/Signup first!"+RESET)

            elif option == "5":
                if self.username != None:
                    self.listChatRooms()
                else:
                    print(RED + "Please Login/Signup first!"+RESET)

            elif option == "6":
                if self.username != None:
                    roomname = input(GREEN + "Enter chatroom name: "+ RESET)
                    self.createChatRoom(
                        roomname,
                    )
                else:
                    print(RED + "Please Login/Signup first!"+RESET)

            elif option == "7":
                if self.username != None:
                    roomname = input(GREEN + "Enter chatroom name: "+ RESET)
                    self.joinChatRoom(roomname)
                else:
                    print(RED + "Please Login/Signup first!"+RESET)
            elif option == "8":
                if self.username != None:
                    self.logout()
                else:
                    print(RED + "Already Logged out!"+RESET)
            elif option =="OK":
                self.acceptChatRequest()
            elif option=="REJECT":
                self.peerServer.isChatRequested = 0
                self.peerServer.connectedPeerSocket.send("REJECT".encode())
            elif int(option) > 9 :
                print(RED + "Invalid Option!"+RESET)
        if option == "9":
            self.exitApp()

    def createAccount(self, username, password):
        message = "JOIN " + username + " " + password
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "join-exists":
            print(RED + "Failed. Account Already Exist :( "+RESET)
        elif response == "join-success":
            print(YELLOW + "Account Created Successfully :) "+RESET)

    def createChatRoom(self, roomname):
        message = "CREATE-CHAT-ROOM" + " " + roomname
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "create-chat-room-exists":
            print(RED + "Failed. Chatroom Already Exist :( "+RESET)
        elif response == "create-chat-room-success":
            print(YELLOW + "Chatroom Created Successfully :) "+RESET)
            self.joinChatRoom(roomname)

    def start_hello_thread(self):
        hello_thread = threading.Thread(target=self.send_hello_message)
        hello_thread.start()

    def send_hello_message(self):
        while self.helloMessageRunFlag:
            try:
                message = "HELLO " + self.username
                self.udpSocket.sendto(
                    message.encode(), (self.serverIP, SERVER_UDP_PORT)
                )
                time.sleep(1)
            except socket.error as e:
                print(RED + f"Error sending 'HELLO' message: {e}"+RESET)
                break

    def logout(self):
        message = "LOGOUT " + self.username
        self.tcpSocket.send(message.encode())
        self.helloMessageRunFlag = False
        self.username = None
        self.peerServerPort = None
        print(YELLOW + "Logged out successfully :) "+RESET)

    def exitApp(self):
        if self.username != None:
            self.logout()
            self.tcpSocket.close()
            self.udpSocket.close()
            print(YELLOW + "Exited successfully :) "+RESET)
        else:
            self.tcpSocket.close()
            self.udpSocket.close()
            print(YELLOW + "Exited successfully :) "+RESET)

    def login(self, username, password, peerServerPort):
        message = "LOGIN " + username + " " + password + " " + peerServerPort
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "login-success":
            self.username = username
            self.peerServerPort = peerServerPort
            self.helloMessageRunFlag = True
            self.peerServer = PS.PeerServer(self.username, int(self.peerServerPort))
            self.peerServer.start()
            self.start_hello_thread()
            print(YELLOW + "Logged in successfully..."+RESET)
        elif response == "login-account-not-exist":
            print(RED + "Failed. Account does not exist :("+RESET)
        elif response == "login-online":
            print(RED + "Account is already online..."+RESET)
        elif response == "login-wrong-credentials":
            print(RED + "Wrong username or password..."+RESET)

    def listOnlineUsers(self):
        message = "LIST-ONLINE-USERS"
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        response = response.strip("[]")
        response = response.split(")")
        mylist = []
        for item in response:
            if item.startswith("("):
                t = item[1:]
                t = t.replace(" ", "")
                t = t.replace("'", "")
                t = t.split(",")
                mylist.append(t)
            elif item.startswith(", ("):
                t = item[3:]
                t = t.replace(" ", "")
                t = t.replace("'", "")
                t = t.split(",")
                mylist.append(t)
        print(tabulate.tabulate(mylist, headers=["username", "ip", "port"]))

    def listChatRooms(self):
        message = "LIST-CHAT-ROOMS"
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        response = response.strip("[]")
        response = response.split(")")
        mylist = []
        for item in response:
            if item.startswith("("):
                t = item[1:]
                t = t.replace(" ", "")
                t = t.replace("'", "")
                t = t.split(",")
                mylist.append(t)
            elif item.startswith(", ("):
                t = item[3:]
                t = t.replace(" ", "")
                t = t.replace("'", "")
                t = t.split(",")
                mylist.append(t)
        print(tabulate.tabulate(mylist, headers=["Room Name", "Users"]))

    def server_notifcation(self):
        while self.chatRoomMessageReceiveFlag:
            peerServerMessage = self.tcpSocket.recv(1024).decode().split()
            if not peerServerMessage:
                continue
            if peerServerMessage[0] == "Leave-chat-room-success":
                print(YELLOW + "Left the chatroom successfully :) ")
                self.chatRoomUsers = None
                self.peerServer.chattingClientName = None
                self.peerServer.isChatRequested = 0
                break
            if peerServerMessage[0] == "NEW-MEMBER-JOINED":
                print(
                    BLUE + peerServerMessage[1] + " joined the chatroom "+RESET
                )
                self.chatRoomUsers.append(
                    (
                        peerServerMessage[1],
                        peerServerMessage[2],
                        int(peerServerMessage[3]),
                    )
                )
            if peerServerMessage[0] == "MEMBER-LEFT":
                print(BLUE + peerServerMessage[1] + " left the chatroom "+RESET)
                for user in self.chatRoomUsers:
                    if user[0] == peerServerMessage[1]:
                        self.chatRoomUsers.remove(user)
                        break

    def receive_messages(self):
        inputs = [self.udpSocket]
        while inputs and self.chatRoomMessageReceiveFlag:
            readable, writable, exceptional = select.select(inputs, [], [], 0.1)
            for sock in readable:
                if sock is self.udpSocket:
                    peerToPeerMessage = (
                        self.udpSocket.recv(1024).decode().split(maxsplit=1)
                    )
                    if peerToPeerMessage is not None:
                        print(
                            CYAN
                            + peerToPeerMessage[0]
                            + ": "
                            + RESET
                            + PURPLE
                            + format_message(peerToPeerMessage[1])+RESET
                        )

    def send_messages(self, message):
        if self.chatRoomUsers is not None:
            for user in self.chatRoomUsers:
                dest_ip = user[1]
                dest_port = user[2]
                self.udpSocket.sendto(
                    str(self.username + " " + message).encode(), (dest_ip, int(dest_port))
                )

    def joinChatRoom(self, roomname):
        message = "JOIN-CHAT-ROOM" + " " + roomname + " " + self.username
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode().split(maxsplit=1)
        if response[0] == "join-chat-room-not-exist":
            print(RED + "Failed. Chatroom does not exist :( ")
        elif response[0] == "join-chat-room-success":
            print(YELLOW + "Chatroom Joined Successfully :) ")
            self.peerServer.chattingClientName = roomname
            self.peerServer.isChatRequested = 1
            self.chatRoomUsers = []
            if len(response) > 1:
                s = response[1]
                if s != "[]":
                    s = s.strip("[]")
                    s = s.split(")")
                    for item in s:
                        if item.startswith("("):
                            t = item[1:]
                            t = t.replace(" ", "")
                            t = t.replace("'", "")
                            t = t.split(",")
                            self.chatRoomUsers.append(t)
                        elif item.startswith(", ("):
                            t = item[3:]
                            t = t.replace(" ", "")
                            t = t.replace("'", "")
                            t = t.split(",")
                            self.chatRoomUsers.append(t)
            self.chatRoomMessageReceiveFlag = True
            receive_thread = threading.Thread(target=self.receive_messages)
            server_notification_thread = threading.Thread(
                target=self.server_notifcation
            )

            receive_thread.start()
            server_notification_thread.start()

            message = input(RESET)
            while not message:
                message = input(RESET)
            while message != ":q":
                self.send_messages(message)
                message = input(RESET)
                while not message:
                    message = input(RESET)
            self.chatRoomMessageReceiveFlag = False
            receive_thread.join()
            self.leaveChatRoom(roomname)
            server_notification_thread.join()

    def leaveChatRoom(self, roomname):
        message = "LEAVE-CHAT-ROOM" + " " + roomname + " " + self.username
        self.tcpSocket.send(message.encode())

    def startOneToOneChat(self):
        response=self.searchUser()
        if response=="user-not-online":
            print(RED + "Failed. User is not online :( "+RESET)
        else:
            print(YELLOW + "User is online :) "+RESET)
            response=response.split()
            self.peerClient = PC.PeerClient(
                response[0], int(response[1]), self.username, self.peerServer, None
            )
            self.peerClient.start()
            self.peerClient.join()
            self.peerClient = None

        

    def searchUser(self):
        user= input(GREEN + "Enter username: "+ RESET)
        while user==self.username:
            print(RED + "You can't chat with yourself :( "+RESET)
            user= input(GREEN + "Enter username: "+ RESET)
        message = "SEARCH-USER" + " " + user
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        return response
    
    def acceptChatRequest(self):
        message="OK "+ self.username
        self.peerServer.connectedPeerSocket.send(message.encode())
        self.peerClient = PC.PeerClient(
                self.peerServer.connectedPeerIP, int(self.peerServer.connectedPeerPort), self.username, self.peerServer, "OK"
            )
        self.peerClient.start()
        self.peerClient.join()


Peer()
