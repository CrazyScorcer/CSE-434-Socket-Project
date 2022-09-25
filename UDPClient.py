from socket import *
import pickle
#class User():
#	def _init_(self, handle, address):
#		self.handle = ""
#		self.address = ""
class Follow:
	def __init__(self, user, target):
		self.user = user
		self.target = target

serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000

clientSocket = socket(AF_INET, SOCK_DGRAM)

command = ""
while command != 'exit':
    command = input('Enter command: ')
    cmdList = command.split(" ")
    if cmdList[0] == 'Follow':
        msg = Follow(cmdList[1], cmdList[2])
        message = pickle.dumps(msg)

#print('before sending to server ', msg.user, ' ', msg.target)

        clientSocket.sendto(message,(serverIP, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
#print(pickle.loads(modifiedMessage).user, ' ', pickle.loads(modifiedMessage).target)
    
clientSocket.close()
