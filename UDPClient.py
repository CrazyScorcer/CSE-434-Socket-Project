from socket import *
from collections import OrderedDict
import pickle
import threading
import sys

class User():
	def __init__(self,handle,address):
		self.handle = handle
		self.address = address
class Req:
	def __init__(self, user, target):
		self.user = user
		self.target = target
class ExitCode:
	def __init__(self, name, follow):
		self.name = name
		self.follow = follow
class Delete:
	def __init__(self, delete):
		self.delete = delete

following = [] #Lists of users that client user is foloowing

serverIP = sys.argv[1] # take in command server ip
serverPort = int(sys.argv[2]) # take in command line port

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientPort = int(sys.argv[3]) # take in command line port
clientIP = gethostbyname(getfqdn())
clientAddr = (clientIP,clientPort)
clientSocket.bind(clientAddr)

#listenSocket = socket(AF_INET, SOCK_DGRAM)
#listenPort = int(sys.argv[4]) # take in command line port
#listenIP = gethostbyname(getfqdn())
#listenAddr = (listenIP, listenPort)
#listenSocket.bind(listenAddr)

def clientStart():
	userHandle = input("Insert Handle: ")
	while True:
		#check to see if handle is longer than 15 characters
		while len(userHandle) > 15:
			userHandle = input("Handle too long. Try Again. ")
		#sends handle to server to register
		clientData = ["Register" , userHandle]
		clientSocket.sendto(pickle.dumps(clientData),(serverIP, serverPort))
		serverData, serverAddress = clientSocket.recvfrom(2048)
		#if the handle doesn't exist, move to ask commands from user
		if (serverData.decode() == "Success"):
			print("Success")
			break
		#otherwise ask user again for handle
		userHandle = input("Handle Already Exists. Try Again. ")
	while True:
		clientData = []
		listenChange()
		userInput = input("Type command: ")
		clientData.append(userInput)
		listenChange()
		if userInput == "Query Handles":
			#query the server for handles and returns list of handles currently on the server	
			clientSocket.sendto(pickle.dumps(clientData), serverAddress)
			serverData, serverAddress = clientSocket.recvfrom(2048)
			serverData = pickle.loads(serverData)
			print("Total Users: ", serverData[0])
			userList = serverData[1]
			for x in userList:
				print(x.handle)
			
		elif userInput == "Follow":
			followTarget = input('Please type the name of the person you want to follow: ')
			clientData.append(Req(userHandle, followTarget))
			#tries to find the followTarget to be follow in clientSide following lists lists
			try:
				unique = following.index(followTarget)
			#if error, then followTarget doesn't exist in following list, therefore append and sort
			except ValueError:
				following.append(followTarget)
				following.sort()

			clientSocket.sendto(pickle.dumps(clientData),(serverIP, serverPort))
			#waits for server response
			serverData, serverAddress = clientSocket.recvfrom(2048)
			print(serverData.decode())
			if serverData.decode() == "SUCCESS":
				print(userHandle , ' is now following ', followTarget)
				print("New following list: ", following)
			else:
				print("User is already following: ", followTarget)
		elif userInput == "Drop":
			dropTarget = input('Please type the name of the person you want to unfollow: ')
			clientData.append(Req(userHandle , dropTarget))
			#checks if dropTarget is in the list of users that is currently being followed
			try:
				exists = following.remove(dropTarget)
				following.sort()
				print('New following list: ', following)
				clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
				serverData, serverAddress = clientSocket.recvfrom(2048)
				print(serverData.decode())
			except ValueError:
				print('You are not following that person')
		elif userInput == "Tweet":
			print("Functionallity not implemented yet")
		elif userInput == "Exit":
		#sends exit request to server
			clientData.append(ExitCode(userHandle , following))
			clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
			finalMsg, serverAddress = clientSocket.recvfrom(2048)
			print(finalMsg.decode())
			break
		else:
			print("Invalid Command")
#temporary function so that client and server share the same info
def listenChange():
	clientData = ["Query Handles"]
	clientSocket.sendto(pickle.dumps(clientData),(serverIP, serverPort))
	serverData, serverAddress = clientSocket.recvfrom(2048)
	serverData = pickle.loads(serverData)
	for followingUser in following:
		inUserLists = False
		if len(serverData[1]) != 0:
			for serverUsers in serverData[1]:
				if followingUser == serverUsers.handle:
					inUserLists = True
					break
			if not inUserLists:
				following.remove(followingUser)

#2nd thread function to listen for when a user exits
#def listening():
#	while True:
#		message, serverAddress = listenSocket.recvfrom(2048)
#		deleteMsg = pickle.loads(message)
#		print('server sent a msg to ', deleteMsg.follower, ' to go and delete ', deleteMsg.name, ' but not rlly tho bc this is going to just one port but at least the delete msg is correct')


#clientSocket.close()
cmdPort = threading.Thread(target=clientStart, args=())
cmdPort.start()

#listeningPort = threading.Thread(target=listening, args=(), daemon=True)
#listeningPort.start()

cmdPort.join()
clientSocket.close()
#listenSocket.close()

print('client terminated')
