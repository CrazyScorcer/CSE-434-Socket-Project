from asyncio import Handle
from socket import *
from collections import OrderedDict
import pickle
import threading
import sys
from turtle import update

class User():
	def __init__(self,handle,mainAddress,listenAddress):
		self.handle = handle
		self.mainAddress = mainAddress
		self.listenAddress = listenAddress
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

class SetUp:
	def __init__(self, sender, left, right):
		self.sender = sender
		self.left = left
		self.right = right	

class Tweet:
	def __init__(self, sender, tweet):
		self.sender = sender
		self.tweet = tweet

class Update:
	def __init__(self, side, ringOwner, newUser ):
		self.side = side
		self.ringOwner = ringOwner
		self.newUser = newUser

class Neighbors:
	def __init__(self, leftUser, rightUser ):
		self.leftUser = leftUser
		self.rightUser = rightUser

following = [] #Lists of users that client user is foloowing

serverIP = sys.argv[1] # take in command server ip
serverPort = int(sys.argv[2]) # take in command line port

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientPort = int(sys.argv[3]) # take in command line port
clientIP = gethostbyname(getfqdn())
clientAddr = (clientIP,clientPort)
clientSocket.bind(clientAddr)

listenSocket = socket(AF_INET, SOCK_DGRAM)
listenPort = int(sys.argv[4]) # take in command line port
listenIP = gethostbyname(getfqdn())
listenAddress = (listenIP, listenPort)
listenSocket.bind(listenAddress)

logicRings = {} #logic rings the user is apart of

userHandle = ""

def clientStart():
	global userHandle
	userHandle = input("Insert Handle: ")
	while True:
		#check to see if handle is longer than 15 characters
		while len(userHandle) > 15:
			userHandle = input("Handle too long. Try Again. ")
		#sends handle to server to register
		print("Client sent register command")
		print("Waiting for server...")
		clientData = ["Register" , userHandle, listenAddress]
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
		#listenChange()
		userInput = input("Type command: ")
		clientData.append(userInput)
		#listenChange()
		if userInput == "Query Handles":
			#query the server for handles and returns list of handles currently on the server	
			print("Sent query request to server")
			print("Waiting for server...")
			clientSocket.sendto(pickle.dumps(clientData), serverAddress)
			serverData, serverAddress = clientSocket.recvfrom(2048)
			serverData = pickle.loads(serverData)
			print("Server has sent data back. Loading...")
			if serverData[0] != -1:
				print("Total Users: ", serverData[0])
				userList = serverData[1]
				for x in userList:
					print(x.handle)
			else:
				print("Server is not currently accepting any commands")
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

			print("Sending follow request to server")
			print("Waiting for server...")
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
				print("Sending drop request to server")
				print("Waiting for server")
				clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
				serverData, serverAddress = clientSocket.recvfrom(2048)
				print(serverData.decode())
			except ValueError:
				print('You are not following that person')
		elif userInput == "Tweet":
			tweet = input("Type your tweet: ")
			while len(tweet) > 140:
				tweet = input("Tweet too long. Try again. ")
			clientData.append(userHandle)
			clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
			serverData, serverAddress = clientSocket.recvfrom(2048)
			serverData = pickle.loads(serverData) #list of User objects that are following tweeter
			#construct a follower ring if one hasn't been constructed yet
			if (userHandle in logicRings):
				prev = 0
				after = 2
				for follower in serverData: 
					if follower.handle != userHandle:
						leftNeighbor = serverData[prev]
						#sets right neighbor as next user in list
						if after != len(serverData):
							rightNeighbor = serverData[after]
							after = after + 1
						#makes last follower's right neighbor the tweeter
						else:
							rightNeighbor = serverData[0]
							ownSetup = SetUp(userHandle, follower, serverData[1]) # tweeter, left neighbor, right neighbor
							clientSocket.sendto(pickle.dumps(ownSetup), listenAddress)
						
						prev = prev + 1
						setup = SetUp(userHandle, leftNeighbor, rightNeighbor)
						clientSocket.sendto(pickle.dumps(setup), serverData[prev].listenAddress)		
			
			tweetMsg = Tweet(userHandle, tweet)
			clientSocket.sendto(pickle.dumps(tweetMsg), serverData[1].listenAddress)	
		#sends exit request to server
		elif userInput == "Exit":
			#removes user from logic rings
			if (len(logicRings) != 0):
				for x in logicRings:
					#fix this!!!!!!!!!!!!!!!!!!!!!!!!!
					updateData = Update("Change Right", x, logicRings[x].rightUser)
					clientSocket.sento(pickle.dumps(updateData), logicRings[x].leftUser.listenAddress)
					recievedMsg, senderAddr = clientSocket.recvfrom(2048)
					print(recievedMsg)
					updateData = Update("Change left", x, logicRings[x].leftUser)
					clientSocket.sento(pickle.dumps(updateData), logicRings[x].rightUser.listenAddress)
					recievedMsg, senderAddr = clientSocket.recvfrom(2048)
					print(recievedMsg)
			
			clientData.append(ExitCode(userHandle , following))
			print("Sending exit request to server")
			clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
			print("Waiting for server")
			finalMsg, serverAddress = clientSocket.recvfrom(2048)
			print(finalMsg.decode())
			break
		else:
			print("Invalid Command")

#Listens for
def listenChange():
	while True:
		#print("right is waiting")
		receivedMsg, senderAddr = listenSocket.recvfrom(2048)
		receivedMsg = pickle.loads(receivedMsg)
		if type(receivedMsg) is Delete:
			following.remove(receivedMsg.delete)
			print("\nfollowing is now", following)
			print("Type command: ")

		if type(receivedMsg) is SetUp:
			userNeighbors = Neighbors(receivedMsg.left, receivedMsg.right)
			logicRings.update({receivedMsg.sender: userNeighbors})
			print("Set up of left and right neighbors complete")

		if type(receivedMsg) is Tweet:
			#print(type(leftN))
			#global leftN	
			global userHandle
			if receivedMsg.sender == userHandle:
				clientData = []
				clientData.append("End Tweet")
				listenSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
			else:
				print(receivedMsg.sender, f" sent a tweet by{logicRings[receivedMsg.handle].leftNeighbor.handle} : ", receivedMsg.tweet)	
				listenSocket.sendto(pickle.dumps(receivedMsg), logicRings[receivedMsg.handle].rightNeighbor.listenAddress)
			print("Type command: ")
			
		if type(receivedMsg) is Update:
			if (receivedMsg.side == "Change Right"):
				logicRings[receivedMsg.ringOwner].rightNeighbor = receivedMsg.newUser
				listenSocket.sendto(pickle.dumps(f"{userHandle}'s right address changed"), senderAddr)
			else:
				logicRings[receivedMsg.ringOwner].leftNeighbor = receivedMsg.newUser
				listenSocket.sendto(pickle.dumps(f"{userHandle}'s left address changed"), senderAddr)
			
startListening = threading.Thread(target=listenChange, args=(), daemon=True)
startListening.start()
print("right is now listening")
cmdPort = threading.Thread(target=clientStart, args=())
print("starting cmd")
cmdPort.start()

cmdPort.join()
clientSocket.close()

print('client terminated')
