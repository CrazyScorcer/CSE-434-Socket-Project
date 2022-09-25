from http import server
from socket import *
import pickle
class Follow:
	def __init__(self, user, target):
		self.user = user
		self.target = target


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
serverAddress = (serverIP,serverPort)
serverSocket.bind(serverAddress)

followerLists = []
followingA = []
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
    if type(modifiedMessage) is Follow :
        index = registered.index(modifiedMessage.target)
        followerLists[index].append(modifiedMessage.user)
        followerLists[index].sort()
    print('after receiving msg ', followerLists) 
    serverSocket.sendto(pickle.dumps(modifiedMessage), clientAddress)
