from socket import *
from collections import OrderedDict
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
class Delete:
	def __init__(self, delete):
		self.delete = delete
  
userLists = [] # = registered = ['A', 'B', 'C']
userFollowers = {} # list containing lists for each user's followers
 
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
serverAddress = (serverIP,serverPort)
serverSocket.bind(serverAddress)

def serverStart():
    print(f"{serverAddress}:Server Started")
    while True:
        #waits for a client to send packet
        clientData, clientAddress = serverSocket.recvfrom(2048)
        clientData = pickle.loads(clientData)
        if clientData[0] == "Register":
                clientRegister(clientData[1],clientAddress)
        elif clientData[0] == "Query Handles":
                queryHandles(clientAddress)
        elif clientData[0] == "Follow":
                followHandle(clientData[1],clientAddress)
        elif clientData[0] == "Drop":
                dropHandle(clientData[1],clientAddress)
        elif clientData[0] == "Tweet":
                print("Functionallity not implemented yet")
        elif clientData[0] == "Exit":
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
    global userFollowers
    userFollowers[handle] = []
    userFollowers = OrderedDict(sorted(userFollowers.items(), key=lambda k:k[0]))
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
    #attempts to find user in following list associate with user
    global userFollowers
    try:
        duplicate = userFollowers[req.target].index(req.user)
    #if user is not following then add to list and sort
    except ValueError:
        userFollowers[req.target].append(req.user)
        userFollowers[req.target].sort()
        returnMsg = 'SUCCESS'
    print('User following list after receiving follow request', userFollowers) 
    if returnMsg != 'SUCCESS':
           returnMsg = 'FAILURE'
    serverSocket.sendto(returnMsg.encode(), clientAddress)
   
def dropHandle(req,clientAddress):
    #finds the index of target to be droped
    #attempts to remove user in following list associate with user
    global userFollowers
    try:
        userFollowers[req.target].remove(req.user)
        userFollowers[req.target].sort()
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
    global userFollowers
    for following in exitCode.follow:
        userFollowers[following].remove(exitCode.name)
        userFollowers[following].sort()
    #find index of user to exit
    deleteList = userLists.index(next(x for x in userLists if exitCode.name == x.handle))
    #removes user from other user's clientside following list
#    for follower in userFollowers[exitCode.name]:
#        listenAddress = next(x for x in userLists if follower == x.handle).address
#        deleteMsg = pickle.dumps(Delete(exitCode.name))
#        serverSocket.sendto(deleteMsg, listenAddress)
    userFollowers.pop(exitCode.name)
    userLists.pop(deleteList)
    print('User following list after receiving exit request ', userFollowers)
    finalMsg = 'User successfully removed from server'
    serverSocket.sendto(finalMsg.encode(), clientAddress)


serverStart()
