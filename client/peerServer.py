from socket import *
import threading
import select

from CLI import *


class PeerServer(threading.Thread):
    def __init__(self, username, peerServerPort):
        threading.Thread.__init__(self)
        self.username = username
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        self.peerServerPort = peerServerPort
        self.isChatRequested = 0
        self.connectedPeerSocket = None
        self.connectedPeerIP = None
        self.connectedPeerPort = None
        self.isOnline = True
        self.chattingClientName = None

    def run(self):
        print(YELLOW+ "Peer server started..."+RESET)
        hostname = gethostname()
        try:
            self.peerServerHostname = gethostbyname(hostname)
        except gaierror:
            import netifaces as ni

            self.peerServerHostname = ni.ifaddresses("en0")[ni.AF_INET][0]["addr"]

        self.tcpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
        self.tcpServerSocket.listen(4)
        inputs = [self.tcpServerSocket]
        while inputs and self.isOnline:
            try:
                readable, writable, exceptional = select.select(inputs, [], [])
                for s in readable:
                    if s is self.tcpServerSocket:
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        if self.isChatRequested == 0:
                            print("\n"+BLUE+self.username + " is connected from " + str(addr))
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    else:
                        messageReceived = s.recv(1024).decode()
                        if (
                            len(messageReceived) > 11
                            and messageReceived[:12] == "CHAT-REQUEST"
                        ):
                            if s is self.connectedPeerSocket:
                                messageReceived = messageReceived.split()
                                self.connectedPeerPort = int(messageReceived[1])
                                self.chattingClientName = messageReceived[2]
                                print(BLUE+
                                    "Incoming chat request from "
                                    + self.chattingClientName
                                    + " >> "+RESET
                                )
                                print(YELLOW+"Enter OK to accept or REJECT to reject:  "+RESET)
                                self.isChatRequested = 1
                            elif (
                                s is not self.connectedPeerSocket
                                and self.isChatRequested == 1
                            ):
                                message = "BUSY"
                                s.send(message.encode())
                                inputs.remove(s)
                        elif messageReceived == "OK":
                            self.isChatRequested = 1
                        elif messageReceived == "REJECT":
                            self.isChatRequested = 0
                            inputs.remove(s)
                        elif messageReceived[:2] != ":q" and len(messageReceived) != 0:
                            messageReceived = format_message(messageReceived)
                            print(CYAN+self.chattingClientName + ": "+PURPLE + messageReceived+RESET)
                        elif messageReceived[:2] == ":q":
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            if len(messageReceived) == 2:
                                print(BLUE+"User you're chatting with ended the chat"+RESET)
                                print(YELLOW+"Press enter to quit the chat: "+RESET)
                        elif len(messageReceived) == 0:
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            print(RED+"User you're chatting with suddenly ended the chat"+RESET)
                            print(YELLOW+"Press enter to quit the chat: "+RESET)
            except OSError as oErr:
                print("OSError: {0}".format(oErr))
            except ValueError as vErr:
                print("ValueError: {0}".format(vErr))
