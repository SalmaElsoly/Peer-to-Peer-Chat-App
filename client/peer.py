from socket import *

class Peer:

  def __init__(self):
    # ??? serverIP = 'localhost' 
    self.serverIP = input("Enter Server IP: ")
    self.serverPort = 5050
    self.tcpSocket = socket(AF_INET, SOCK_STREAM)
    self.tcpSocket.connect((self.serverIP, self.serverPort))
  
  def createAccount(self, username, password):
    message = "JOIN " + username + " " + password
    self.tcpSocket.send(message.encode())
    response = self.tcpSocket.recv(1024).decode()
    if response == "join-exists":
      print("Failed. Account Already Exist :( ")
    elif response == "join-success":
      print("Account Created Successfully :) ")
    
