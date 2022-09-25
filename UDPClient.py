from collections import UserList
from socket import *
import pickle

followedList = []

class User():
    def __init__(self,handle,address):
        self.handle = handle
        self.address = address

clientSocket = socket(AF_INET, SOCK_DGRAM) # UDP Socket
#serverIP = input("Server IP:") # put in final program
#serverPort = input("Server Port") # put in final program

serverIP = gethostbyname(gethostname()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000

bufferSize = 2024 #amount of bytes to be sent/received
def clientStart():
    userHandle = input("Insert Handle: ")
    while True:
        while len(userHandle) > 15:
            userHandle = input("Handle too long. Try Again. ")
        
        clientData = ["Register" , userHandle]
        clientSocket.sendto(pickle.dumps(clientData),(serverIP, serverPort))
        serverData, serverAddress = clientSocket.recvfrom(bufferSize)

        if (pickle.loads(serverData) == "Success"):
            print(pickle.loads(serverData))
            break
        
        userHandle = input("Handle Already Exists. Try Again. ")
    while True:
        clientData = []
        userInput = input("Type command: ")
        match userInput:
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
                print("Functionallity not implemented yet")
            case "Drop":
                print("Functionallity not implemented yet")
            case "Tweet":
                print("Functionallity not implemented yet")
            case "Exit":
                print("Functionallity not implemented yet")
                break
            case _:
                print("Invalid Command")
    
clientStart()
clientSocket.close()


