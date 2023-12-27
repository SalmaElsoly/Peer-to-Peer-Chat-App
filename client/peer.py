import select
import socket
import threading
import time
import tabulate
import msvcrt
import re
import json

import peerServer as PS
import peerClient as PC


def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
        return False  # The password must contain at least one special character
    if re.search(r"\s", password):
        return False  # The password must not contain any whitespace characters
    return True


"""colors for the output"""
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"


""" function to get password from user without showing it on screen """


def get_password(prompt=GREEN + "Enter password: "):
    print(prompt, end="", flush=True)
    password = ""
    while True:
        key = msvcrt.getch()
        if key == b"\r":  # Enter key pressed
            break
        if key == b"\x08":  # Backspace key pressed
            password = password[:-1]
            print("\b \b", end="", flush=True)  # Erase previous character
        else:
            password += key.decode()
            print("*", end="", flush=True)
    print()
    return password


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
        self.chatRoomMessageReceiveFlag=False
        option = 0
        while option != 9:
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
            9. Exit"""
            )
            option = int(input(GREEN + "Enter your option: "))
            if option == 1:
                username = input(GREEN + "Enter username: ")
                password = get_password()
                peerServerPort = input(GREEN + "Enter your port number: ")
                self.login(username, password, peerServerPort)
            elif option == 2:
                username = input(GREEN + "Enter username: ")
                password = get_password()
                while not validate_password(password):
                    print(
                        RED
                        + "Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character"
                    )
                    password = get_password()
                self.createAccount(username, password)
            elif option == 3:
                if self.username != None:
                    self.listOnlineUsers()
                else:
                    print(RED + "Please Login/Signup first!")
            elif option == 4:
                if self.username != None:
                    self.startOneToOneChat()
                else:
                    print(RED + "Please Login/Signup first!")

            elif option == 5:
                if self.username != None:
                    self.listChatRooms()
                else:
                    print(RED + "Please Login/Signup first!")

            elif option == 6:
                if self.username != None:
                    roomname = input(GREEN + "Enter chatroom name: ")
                    self.createChatRoom(
                        roomname,
                    )
                else:
                    print(RED + "Please Login/Signup first!")

            elif option == 7:
                if self.username != None:
                    roomname = input(GREEN + "Enter chatroom name: ")
                    self.joinChatRoom(roomname)
                else:
                    print(RED + "Please Login/Signup first!")
            elif option == 8:
                if self.username != None:
                    self.logout()
                else:
                    print(RED + "Already Logged out!")
            elif option > 9:
                print(RED + "Invalid option...")
        if option == 9:
            self.exitApp()

    def createAccount(self, username, password):
        message = "JOIN " + username + " " + password
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "join-exists":
            print(RED + "Failed. Account Already Exist :( ")
        elif response == "join-success":
            print(YELLOW + "Account Created Successfully :) ")

    def createChatRoom(self, roomname):
        message = "CREATE-CHAT-ROOM" + " " + roomname
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "create-chat-room-exists":
            print(RED + "Failed. Chatroom Already Exist :( ")
        elif response == "create-chat-room-success":
            print(YELLOW + "Chatroom Created Successfully :) ")
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
                print(RED + f"Error sending 'HELLO' message: {e}")
                break

    def logout(self):
        message = "LOGOUT " + self.username
        self.tcpSocket.send(message.encode())
        self.helloMessageRunFlag = False
        self.username = None
        self.peerServerPort = None
        print(YELLOW + "Logged out successfully :) ")

    def exitApp(self):
        if self.username != None:
            self.logout()
            self.tcpSocket.close()
            self.udpSocket.close()
            print(YELLOW + "Exited successfully :) ")
        else:
            self.tcpSocket.close()
            self.udpSocket.close()
            print(YELLOW + "Exited successfully :) ")

    def login(self, username, password, peerServerPort):
        message = "LOGIN " + username + " " + password + " " + peerServerPort
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "login-success":
            self.username = username
            self.peerServerPort = peerServerPort
            self.peerServer = PS.PeerServer(self.username, int(self.peerServerPort))
            self.peerServer.start()
            self.helloMessageRunFlag = True
            self.start_hello_thread()
            print(YELLOW + "Logged in successfully...")
        elif response == "login-account-not-exist":
            print(RED + "Failed. Account does not exist :(")
        elif response == "login-online":
            print(RED + "Account is already online...")
        elif response == "login-wrong-credentials":
            print(RED + "Wrong username or password...")

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
        print(response)
        print(tabulate.tabulate(mylist, headers=["Room Name", "Users"]))

    def receive_messages(self):
        while self.chatRoomMessageReceiveFlag:
            peerToPeerMessage = self.peerServer.recieve_message()
            if peerToPeerMessage is not None:
                if peerToPeerMessage[0] == "MESSAGE":
                    print(
                        BOLD
                        + peerToPeerMessage[1]
                        + ": "
                        + peerToPeerMessage[2]
                        + RESET
                    )
            peerServerMessage = self.tcpSocket.recv(1024).decode().split()
            if peerServerMessage[0] == "NEW-MEMBER-JOINED":
                print(
                    YELLOW + "New member joined the chatroom: " + peerServerMessage[1]
                )
                self.peerClient.chatRoomUsers.append((peerServerMessage[1],peerServerMessage[2],int(peerServerMessage[3])))
            if peerServerMessage[0] == "LEAVE-CHAT-ROOM":
                print(YELLOW + "Member left the chatroom: " + peerServerMessage[1])
                del self.peerClient.chatRoomUsers[peerServerMessage[1]]

    def send_messages(self, roomname):
        while True:
            message=input()
            if message == "exit":
                self.leaveChatRoom(roomname)
            self.peerClient.send_message(message)

    def joinChatRoom(self, roomname):
        message = (
            "JOIN-CHAT-ROOM"
            + " "
            + roomname
            + " "
            + self.username
            + " "
            + self.peerServer.peerServerIP
            + " "
            + self.peerServerPort
        )
        self.tcpSocket.send(message.encode())
        print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        response = self.tcpSocket.recv(1024).decode().split(maxsplit=1)
        print("respponse"+str(response))
        if response[0] == "join-chat-room-not-exist":
            print(RED + "Failed. Chatroom does not exist :( ")
        elif response[0] == "join-chat-room-success":
            print(YELLOW + "Chatroom Joined Successfully :) ")
            #chatRoomusers = json.loads(response[1])
            chatRoomUsers=[]
            if len(response) >1:
                s= response[1]
                if s!="[]":
                    s= s.strip("[]")
                    s=s.split(')')
                    for item in s:
                        if item.startswith("("):
                            t=item[1:]
                            t=t.replace(" ","")
                            t=t.replace("'","")
                            t=t.split(",")
                            chatRoomUsers.append(t)
                        elif item.startswith(",("):
                            t=item[2:]
                            t=t.replace(" ","")
                            t=t.replace("'","")
                            t=t.split(",")
                            chatRoomUsers.append(t)
                print(chatRoomUsers)
                # Move this line inside the loop
            self.peerClient = PC.PeerClient(
                self.username, chatRoomUsers
            )
            self.peerClient.start()
            self.chatRoomMessageReceiveFlag=True
            receive_thread = threading.Thread(target=self.receive_messages)
            # send_thread = threading.Thread(
            #     target=self.send_messages, args=(roomname,)
            # )
            receive_thread.start()
            # send_thread.start()

            try:

                while True:
                    message=input()
                    if message == "exit":
                        self.chatRoomMessageReceiveFlag=False
                        receive_thread.join()
                        self.peerClient.chatRoomUsers={}
                        self.peerClient.stop()
                        self.leaveChatRoom(roomname)
                        break
                    self.peerClient.send_message(message)
            except Exception as e:
                print(f"An error occurred: {e}")

    def leaveChatRoom(self, roomname):
        message = "LEAVE-CHAT-ROOM" + " " + roomname + " " + self.username
        self.tcpSocket.send(message.encode())
        print("before response")
        response = self.tcpSocket.recv(1024).decode()
        print("resp"+response)
        if response == "Leave-chat-room-success":
            print(YELLOW + "Left the chatroom successfully :) ")
            # self.peerClient.chatRoomUsers = {}
            # self.peerClient.stop()
        elif response == "leave-chat-room-not successful":
            print(RED + "couldn't leave chat room :( ")


Peer()
