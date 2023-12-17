import socket
import threading
import time
import tabulate
import msvcrt
import re


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
    if re.search("\s", password):
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
        self.username = None
        self.helloMessageRunFlag = None
        option = 0
        while option != 8:
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
            8. Logout"""
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
                self.listOnlineUsers()
            elif option == 4:
                self.startOneToOneChat()
            elif option == 5:
                self.listChatRooms()
            elif option == 6:
                self.createChatRoom()
            elif option == 7:
                self.joinChatRoom()
            elif option >= 9:
                print(RED + "Invalid option...")
        if option == 8:
            self.logout()

    def createAccount(self, username, password):
        message = "JOIN " + username + " " + password
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "join-exists":
            print(RED + "Failed. Account Already Exist :( ")
        elif response == "join-success":
            print(YELLOW + "Account Created Successfully :) ")

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
        self.tcpSocket.close()
        self.udpSocket.close()
        print(YELLOW + "Logged out successfully :) ")

    def login(self, username, password, peerServerPort):
        message = "LOGIN " + username + " " + password + " " + peerServerPort
        self.tcpSocket.send(message.encode())
        response = self.tcpSocket.recv(1024).decode()
        if response == "login-success":
            self.username = username
            self.peerServerPort = peerServerPort
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


print(socket.gethostbyname(socket.gethostname()))
Peer()
