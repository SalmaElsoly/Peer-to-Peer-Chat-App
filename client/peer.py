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

  def logoutUser(self):
    message = "LOGOUT " + self.username;
    self.tcpSocket.send(message.encode())
    self.tcpSocket.close()
    self.udpSocket.close()
    print("Logged out successfully :) ")



    
