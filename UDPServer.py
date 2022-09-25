from http import server
from socket import *
import pickle
class Req:
	def __init__(self, user, target, reqType):
		self.user = user
		self.target = target
		self.reqType = reqType

class ExitCode:
	def __init__(self, name, follow):
		self.name = name
		self.follow = follow

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
serverAddress = (serverIP,serverPort)
serverSocket.bind(serverAddress)

followerLists = []
followingA = ['C']
followingB = []
followingC = []
followerLists.append(followingA)
followerLists.append(followingB)
followerLists.append(followingC)

registered = ['A', 'B', 'C']

print('The server is ready to receive')
while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = pickle.loads(message)
    print('before modification ', followerLists)
    returnMsg = ""
    if type(modifiedMessage) is Req:
       
        index = registered.index(modifiedMessage.target)
        if modifiedMessage.reqType == 'follow':
            try:
                duplicate = followerLists[index].index(modifiedMessage.user)
            except ValueError:
                followerLists[index].append(modifiedMessage.user)
                followerLists[index].sort()
                returnMsg = 'SUCCESS'
   

        elif modifiedMessage.reqType == 'drop':
           try:
              exists = followerLists[index].remove(modifiedMessage.user)
              followerLists[index].sort()
              returnMsg = 'SUCCESS'
              
           except ValueError:
               print('not even following that person in the first place')  
        print('after receiving msg ', followerLists) 
        if returnMsg != 'SUCCESS':
               returnMsg = 'FAILURE'
        serverSocket.sendto(returnMsg.encode(), clientAddress)
    if type(modifiedMessage) is ExitCode:
        for following in modifiedMessage.follow:
           index = registered.index(following) 
           followerLists[index].remove(modifiedMessage.name)
           followerLists[index].sort()
        deleteList = registered.index(modifiedMessage.name)
        for follower in followerLists[index]:
            listenIP = gethostbyname(getfqdn())
            listenPort = 28002
            deleteMsg = Req(modifiedMessage.name, follower, 'delete')
            serverSocket.sendto(deleteMsg, (listenIP, listenPort))
        followerLists.pop(deleteList)
        print('after exiting, list is ', followerLists)
        finalMsg = 'all delete msgs sent'
        serverSocket.sendto(finalMsg.encode(), clientAddress)
