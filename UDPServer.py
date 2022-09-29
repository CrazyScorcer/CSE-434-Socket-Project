from socket import *
import pickle
import threading

userLists = []
userFollowers = []

serverSocket = socket(AF_INET, SOCK_DGRAM) # UDP Socket
serverIP = gethostbyname(gethostname()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
serverSocket.bind((serverIP,serverPort))

bufferSize = 2024 #amount of bytes to be sent/received

class User():
    def __init__(self,handle,address):
        self.handle = handle
        self.address = address

def serverStart():
    print("Server Started")
    while True:
        #waits for a client to send packet
        clientData, clientAddress = serverSocket.recvfrom(bufferSize)
        clientData = pickle.loads(clientData)
        match clientData[0]:
            case "Register":
                clientRegister(clientData[1],clientAddress)
            case "Query Handles":
                queryHandles(clientAddress)
            case "Follow":
                print("Functionallity not implemented yet")
            case "Drop":
                print("Functionallity not implemented yet")
            case "Tweet":
                print("Functionallity not implemented yet")
#checks if handles exists on the server then registers if it doesn't, otherwise send failure to client for new handle
def clientRegister(handle, clientAddress):
    for x in userLists:
        if x.handle == handle:
            print("Handle already Exists failed to Registered")
            message = "Failure"
            serverSocket.sendto(pickle.dumps(message), clientAddress)
            return
    userLists.append(User(handle, clientAddress))
    print(isinstance(userLists[0],User))
    print("User has been Registered:", handle, clientAddress)
    message = "Success"
    serverSocket.sendto(pickle.dumps(message), clientAddress)
#stores the number of users and the lists of current users in a list to send over
def queryHandles(clientAddress):
    serverData = []
    serverData.append(len(userLists))
    serverData.append(userLists)
    serverSocket.sendto(pickle.dumps(serverData), clientAddress)

serverStart()