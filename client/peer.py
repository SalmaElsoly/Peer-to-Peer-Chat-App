from socket import *
import threading
import time

class Peer:

  def __init__(self):
    # ??? serverIP = 'localhost' 
    self.serverIP = input("Enter Server IP: ")
    self.serverPort = 5050
    self.tcpSocket = socket(AF_INET, SOCK_STREAM)
    self.tcpSocket.connect((self.serverIP, self.serverPort))
    self.udpSocket = socket(AF_INET, SOCK_DGRAM)
    self.udpSocket.bind(('localhost', 0)) 
    self.start_hello_thread()
    self.peerServerPort=None
    self.username=None
    option=0
    while option!=8:
      print(''' Choose one of the following options:
            1. Login
            2. Create Account
            3. List Online Users
            4. Start One to One Chat
            5. List Chat Rooms
            6. Create Chat Room
            7. Join Chat Room
            8. Logout''')
      option = int(input("Enter your option: "))
      if option == 1:
        username = input("Enter username: ")
        password = input("Enter password: ")
        peerServerPort = input("Enter your port number: ")
        self.login(username, password,peerServerPort)
      elif option == 2:
        username = input("Enter username: ")
        password = input("Enter password: ")
        self.createAccount(username, password)
      



  
  def createAccount(self, username, password):
    message = "JOIN " + username + " " + password
    self.tcpSocket.send(message.encode())
    response = self.tcpSocket.recv(1024).decode()
    if response == "join-exists":
      print("Failed. Account Already Exist :( ")
    elif response == "join-success":
      print("Account Created Successfully :) ")

  def start_hello_thread(self):
    hello_thread = threading.Thread(target=self.send_hello_message)
    hello_thread.start()

  def send_hello_message(self):
    while True:
      try:
        message = "HELLO"
        self.udpSocket.sendto(message.encode(), (self.serverIP, self.serverPort))
        time.sleep(1)
      except socket.error as e:
        print(f"Error sending 'HELLO' message: {e}")
        break

  def logout(self):
    message = "LOGOUT " + self.username;
    self.tcpSocket.send(message.encode())
    self.tcpSocket.close()
    self.udpSocket.close()
    print("Logged out successfully :) ")

  def login(self,username,password,peerServerPort):
    message = "LOGIN "+username+" "+password+" "+peerServerPort
    self.tcpSocket.send(message.encode())
    response = self.tcpSocket.recv(1024).decode()
    if response == "login-success":
        self.username=username
        self.peerServerPort=peerServerPort
        print("Logged in successfully...")
    elif response == "login-account-not-exist":
        # print("Account does not exist...")
        print("Wrong username or password...")
    elif response == "login-online":
        print("Account is already online...")
    elif response == "login-wrong-credentials":
        print("Wrong username or password...")
 
    



    
