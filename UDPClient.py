from socket import *
import pickle
import threading
#class User():
#	def _init_(self, handle, address):
#		self.handle = ""
#		self.address = ""
class Req:
	def __init__(self, user, target, reqType):
		self.user = user
		self.target = target
		self.reqType = reqType
class ExitCode:
	def __init__(self, name, follow):
		self.name = name
		self.follow = follow

serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientPort = 28001
clientIP = gethostbyname(getfqdn())
clientAddr = (clientIP,clientPort)
clientSocket.bind(clientAddr)

listenSocket = socket(AF_INET, SOCK_DGRAM)
listenPort = 28002
listenIP = gethostbyname(getfqdn())
listenAddr = (listenIP, listenPort)
listenSocket.bind(listenAddr)

following = []
#command = ""
name = input('Enter handle: ')

def commanding():
    command = ""
    while command != 'exit':
        command = input('Enter command: ')
        if command == 'follow':
            newFollow = input('Please type the name of the person you want to follow: ')
            msg = Req(name, newFollow, 'follow')
            message = pickle.dumps(msg)
            
            try:
                unique = following.index(newFollow)
            except ValueError:

                following.append(newFollow)
                following.sort()
            print(name, ' is following the following ', following)
#print('before sending to server ', msg.user, ' ', msg.target)
            clientSocket.sendto(message,(serverIP, serverPort))
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
#print(pickle.loads(modifiedMessage).user, ' ', pickle.loads(modifiedMessage).target)
            print(modifiedMessage.decode())
        if command == 'drop':
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
    
    msg = ExitCode(name, following)
    message = pickle.dumps(msg)
    clientSocket.sendto(message, (serverIP, serverPort))
    finalMsg, serverAddr = clientSocket.recvfrom(2048)
    print(finalMsg.decode())
    clientSocket.close()

def listening():
    while True:
        message, serverAddress = listenSocket.recvfrom(2048)
        deleteMsg = pickle.loads(message)
        print('server sent a msg to ', deleteMsg.follower, ' to go and delete ', deleteMsg.name, ' but not rlly tho bc this is going to just one port but at least the delete msg is correct') 

cmdPort = threading.Thread(target=commanding, args=())
cmdPort.start()

listeningPort = threading.Thread(target=listening, args=(), daemon=True)
listeningPort.start()

cmdPort.join()
listenSocket.close()
print('client terminated')


