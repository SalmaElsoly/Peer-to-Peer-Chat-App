import select
import socket
import threading
import time
import user_manager as UM

def handle_hello_message(client_username):
    try: 
        tcpThreads[client_username].lastAliveTime = time.time()
    except socket.error:
        print(f"User at {client_address} disconnected.")
        username = UM.get_username(client_address)
        UM.logoutUser(username)
class AliveHandler(threading.Thread):
    def __init__(self,clientUsername):
        threading.Thread.__init__(self)
        self.clientUsername=clientUsername
        self.runFlag=True
    def stopThread(self):
        self.runFlag=False
    def run(self):
        while self.runFlag:
            current_time = time.time()
            if self.runFlag and current_time - tcpThreads[self.clientUsername].lastAliveTime > 3 :
                username = tcpThreads[self.clientUsername].username
                del tcpThreads[self.clientUsername]
                print(f"User at {self.clientUsername} disconnected by alive timeout.")

            # username = UM.get_username(user)
                UM.logoutUser(username)
                self.runFlag=False

            time.sleep(2) #Low CPU Utilization
    

class ClientThread(threading.Thread) :
    def __init__(self,ip,port,clientSocket) -> None:
        super(ClientThread, self).__init__()
        self.ip=ip
        self.port=port
        self.clientSocket=clientSocket
        self.AliveHandler=None
        self.lastAliveTime=None
        self.username=None

    def run(self) -> None:
        self.lock=threading.Lock()
        while True:
            try:
                data = self.clientSocket.recv(1024).decode().split()
                if data[0] == "JOIN":
                    #verify username and create account , username in data[1] and password in data[2]
                    #if username exists return message "join-exists" otherwise create account and return message "join-success"
                    result = UM.createAccount(data[1],data[2])
                    self.clientSocket.send(result.encode())
                elif data[0]=="LOGIN" :
                    #Message: LOGIN <username> <password> <portNumberOfTheClient>
                    result = UM.loginUser(data[1],data[2],self.ip,data[3])
                    if result in {"login-account-not-exist","login-wrong-credentials","login-online"} :
                        self.clientSocket.send(result.encode())
                    elif result == "login-success":
                        self.username=data[1]
                        self.lock.acquire()
                        try:
                            tcpThreads[self.username] = self
                        finally:
                            self.lock.release()
                        self.lastAliveTime=time.time()
                        self.AliveHandler = AliveHandler(self.username)
                        self.AliveHandler.start()
                        
                        self.clientSocket.send(result.encode())
                        print("User :"+self.ip+" is logged in successfully")
                elif data[0]=="LOGOUT":
                    #Message: LOGOUT <username>
                    self.AliveHandler.stopThread();
                    UM.logoutUser(self.username)
                    self.lock.acquire()
                    try:
                        del tcpThreads[self.username]
                    finally:
                        self.lock.release()
                    print(self.ip + ":" + str(self.port) + " is logged out")
                    self.clientSocket.close()
                    
                    break
                elif data[0]=="LIST-ONLINE-USERS":
                    #Message: LIST-ONLINE-USERS
                    self.clientSocket.send(str(UM.getOnlineUsers(self.username)).encode())
                    print("list-users")
                elif data[0]=="CREATE-CHAT-ROOM":
                    #Message: CREATE-CHAT-ROOM <roomName>
                    print("create room")
                elif data[0]=="JOIN-CHAT-ROOM":
                    #Message: JOIN-CHAT-ROOM <roomName>
                    print("join room")
                elif data[0]=="LIST-CHAT-ROOMS":
                    #Message: LIST-CHAT-ROOMS
                    print("list rooms")
            except OSError as oErr:
                print("OSError: {0}".format(oErr)) 
TCPport = 5050
UDPport = 1515
host_ip = socket.gethostbyname(socket.gethostname())

print("Server host IP = "+host_ip)
print("Server port = "+str(TCPport))


tcpThreads = {}
#socket.AF_INET: Specifies the address family (IPv4).
#socket.SOCK_STREAM: Specifies the socket type (TCP).
#socket.SOCK_DGRAM: Datagram-oriented socket (UDP).
try: 
    tcpSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print ("Socket successfully created")
except socket.error as err:
    print (f"socket creation failed with error {err}")
try:
    tcpSocket.bind((host_ip,TCPport))
    udpSocket.bind((host_ip,UDPport))
except socket.error as e:
    print(f"Error binding the server socket: {e}")

tcpSocket.listen(5) # max 5 connections in queue

sockets = [tcpSocket,udpSocket]

while sockets :
    readable, writable, exceptional = select.select(sockets, [], [])
    for sock in readable:
        if sock is tcpSocket:
            client_socket, client_address = tcpSocket.accept()
            # new thread
            print("client_address: "+str(client_address))
            newClientThread=ClientThread(client_address[0],client_address[1],client_socket)
            newClientThread.start()
        if sock is udpSocket:
            #client_address is a tuple containing ip,port
            data, client_address = udpSocket.recvfrom(1024)# Buffer size is 1024 bytes
            # check hello message
            if data.decode().split()[0] == "HELLO":
                handle_hello_message(data.decode().split()[1])