from http import client
from socket import *
import pickle
import threading
#implement userLists object sort
#implement userLists object sort
#implement userLists object sort
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
    
userLists = [] # = registered = ['A', 'B', 'C']
userFollowers = [] # list containing lists for each user's followers
 
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
serverAddress = (serverIP,serverPort)
serverSocket.bind(serverAddress)

def serverStart():
    print("Server Started")
    while True:
        #waits for a client to send packet
        clientData, clientAddress = serverSocket.recvfrom(2048)
        clientData = pickle.loads(clientData)
        match clientData[0]:
            case "Register":
                clientRegister(clientData[1],clientAddress)
            case "Query Handles":
                queryHandles(clientAddress)
            case "Follow":
                followHandle(clientData[1],clientAddress)
            case "Drop":
                dropHandle(clientData[1],clientAddress)
            case "Tweet":
                print("Functionallity not implemented yet")
            case "Exit":
                exitCode(clientData[1],clientAddress)
                
#checks if handles exists on the server then registers if it doesn't, otherwise send failure to client for new handle
def clientRegister(handle, clientAddress):
    for x in userLists:
        if x.handle == handle:
            print("Handle already Exists failed to Registered")
            message = "Failure"
            serverSocket.sendto(message.encode(), clientAddress)
            return
    userLists.append(User(handle, clientAddress))
    print(isinstance(userLists[0],User))
    print("User has been Registered:", handle, clientAddress)
    message = "Success"
    serverSocket.sendto(message.encode(), clientAddress)
#stores the number of users and the lists of current users in a list to send over
def queryHandles(clientAddress):
    serverData = []
    serverData.append(len(userLists))
    serverData.append(userLists)
    serverSocket.sendto(pickle.dumps(serverData), clientAddress)

def followHandle(req,clientAddress):
    #finds the index of target to be followed
    index = userLists.index(next(x for x in userLists if req.target == x.handle))
    #attempts to find user in following list associate with user
    try:
        duplicate = userFollowers[index].index(req.user)
    #if user is not following then add to list and sort
    except ValueError:
        userFollowers[index].append(req.user)
        userFollowers[index].sort()
        returnMsg = 'SUCCESS'
    print('User following list after receiving follow request', userFollowers) 
    if returnMsg != 'SUCCESS':
           returnMsg = 'FAILURE'
    serverSocket.sendto(returnMsg.encode(), clientAddress)
   
def dropHandle(req,clientAddress):
    #finds the index of target to be droped
    index = userLists.index(next(x for x in userLists if req.target == x.handle)) 
    #attempts to remove user in following list associate with user
    try:
        userFollowers[index].remove(req.user)
        userFollowers[index].sort()
        returnMsg = 'SUCCESS'
    #if user is not following then print message
    except ValueError:
        print('not even following that person in the first place')  
    print('User following list after receiving drop request: ', userFollowers) 
    if returnMsg != 'SUCCESS':
        returnMsg = 'FAILURE'
    serverSocket.sendto(returnMsg.encode(), clientAddress)

def exitCode(exitCode,clientAddress):
    #removes user from other user's follower list
    for following in exitCode.follow:
        index = userLists.index(next(x for x in userLists if following == x.handle))
        userFollowers[index].remove(exitCode.name)
        userFollowers[index].sort()
    #find index of user to exit
    deleteList = userLists.index(next(x for x in userLists if exitCode.name == x.handle))
    #removes user from other user's clientside following list
    for follower in userFollowers[deleteList]:
        listenAddress = next(x for x in userLists if follower == x.handle).address
        deleteMsg = Req(exitCode.name, follower, 'delete')
        serverSocket.sendto(deleteMsg, listenAddress)
    userFollowers.pop(deleteList)
    userLists.pop(deleteList)
    print('User following list after receiving exit request ', userFollowers)
    finalMsg = 'User successfully removed from server'
    serverSocket.sendto(finalMsg.encode(), clientAddress)


serverStart()