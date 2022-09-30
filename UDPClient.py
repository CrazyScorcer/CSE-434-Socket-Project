from socket import *
import pickle
import threading
class User():
    def __init__(self,handle,address):
        self.handle = handle
        self.address = address
class Req:
	def __init__(self, user, target, reqType):
		self.user = user
		self.target = target
		self.reqType = reqType
class ExitCode:
	def __init__(self, name, follow):
		self.name = name
		self.follow = follow

following = []

serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientPort = 28001 # add commandline parameters to accept user selected ports
clientIP = gethostbyname(getfqdn())
clientAddr = (clientIP,clientPort)
clientSocket.bind(clientAddr)

listenSocket = socket(AF_INET, SOCK_DGRAM)
listenPort = 28002 # add commandline parameters to accept user selected ports
listenIP = gethostbyname(getfqdn())
listenAddr = (listenIP, listenPort)
listenSocket.bind(listenAddr)

def clientStart():
    userHandle = input("Insert Handle: ")
    while True:
        #check to see if handle is longer than 15 characters
        while len(userHandle) > 15:
            userHandle = input("Handle too long. Try Again. ")
        #sends handle to server to register
        clientData = ["Register" , userHandle]
        clientSocket.sendto(pickle.dumps(clientData),(serverIP, serverPort))
        serverData, serverAddress = clientSocket.recvfrom(bufferSize)
        #if the handle doesn't exist, move to ask commands from user
        if (pickle.loads(serverData) == "Success"):
            print(pickle.loads(serverData))
            break
        #otherwise ask user again for handle
        userHandle = input("Handle Already Exists. Try Again. ")
    while True:
        clientData = []
        userInput = input("Type command: ")
        match userInput:
            #query the server for handles and returns list of handles currently on the server
            case "Query Handles":
                clientData.append(userInput)
                clientSocket.sendto(pickle.dumps(clientData), serverAddress)
                serverData, serverAddress = clientSocket.recvfrom(bufferSize)
                serverData = pickle.loads(serverData)
                print("Total Users: ", serverData[0])
                userList = serverData[1]
                for x in userList:
                    print(x.handle)
                break
            case "Follow":
                newFollow = input('Please type the name of the person you want to follow: ')
                msg = Req(name, newFollow, 'follow')
                message = pickle.dumps(msg)

                try:
                    unique = following.index(newFollow)
                except ValueError:

                    following.append(newFollow)
                    following.sort()
                print(name, ' is following the following ', following)
                clientSocket.sendto(message,(serverIP, serverPort))
                modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
                print(modifiedMessage.decode())
            case "Drop":
                dropReq = input('Please type the name of the person you want to unfollow: ')
                msg = Req(name, dropReq, 'drop')
                message = pickle.dumps(msg)
                try:
                    exists = following.remove(dropReq)
                    following.sort()
                    print('new list of following: ', following)
                    clientSocket.sendto(message, (serverIP, serverPort))
                    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
                    print(modifiedMessage.decode())
                except ValueError:
                print('You are not following that person')
            case "Tweet":
                print("Functionallity not implemented yet")
            case "Exit":
                msg = ExitCode(name, following)
                message = pickle.dumps(msg)
                clientSocket.sendto(message, (serverIP, serverPort))
                finalMsg, serverAddr = clientSocket.recvfrom(2048)
                print(finalMsg.decode())
                break
            case _:
                print("Invalid Command")

def listening():
    while True:
        message, serverAddress = listenSocket.recvfrom(2048)
        deleteMsg = pickle.loads(message)
        print('server sent a msg to ', deleteMsg.follower, ' to go and delete ', deleteMsg.name, ' but not rlly tho bc this is going to just one port but at least the delete msg is correct'


clientSocket.close()
cmdPort = threading.Thread(target=commanding, args=())
cmdPort.start()

listeningPort = threading.Thread(target=listening, args=(), daemon=True)
listeningPort.start()

clientStart()

cmdPort.join()
listenSocket.close()

print('client terminated')