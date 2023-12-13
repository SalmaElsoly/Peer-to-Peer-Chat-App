import socket
import threading
import time
import tabulate

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
    self.peerServerPort=None
    self.username=None
    self.helloMessageRunFlag=None
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
    if option == 8:
      self.logout()
      



  
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
    while self.helloMessageRunFlag:
      try:
        message = "HELLO "+self.username
        self.udpSocket.sendto(message.encode(), (self.serverIP, SERVER_UDP_PORT))
        time.sleep(1)
      except socket.error as e:
        print(f"Error sending 'HELLO' message: {e}")
        break

  def logout(self):
    message = "LOGOUT " + self.username;
    self.tcpSocket.send(message.encode())
    self.helloMessageRunFlag=False
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
        self.helloMessageRunFlag=True
        self.start_hello_thread()
        print("Logged in successfully...")
    elif response == "login-account-not-exist":
        # print("Account does not exist...")
        print("Wrong username or password...")
    elif response == "login-online":
        print("Account is already online...")
    elif response == "login-wrong-credentials":
        print("Wrong username or password...")
  def listOnlineUsers(self):
    message = "LIST-ONLINE-USERS"
    self.tcpSocket.send(message.encode())
    response = self.tcpSocket.recv(1024).decode()
    response = response.strip("[]")
    response=response.split(')')
    mylist=[]
    for item in response:
      if item.startswith("("):
          t=item[1:]
          t=t.replace(" ","")
          t=t.replace("'","")
          t=t.split(",")
          mylist.append(t)
      elif item.startswith(", ("):
          t=item[3:]
          t=t.replace(" ","")
          t=t.replace("'","")
          t=t.split(",")
          mylist.append(t)
    print(tabulate.tabulate(mylist,headers=["username","ip","port"]))
 
    

print(socket.gethostbyname(socket.gethostname()))
Peer()