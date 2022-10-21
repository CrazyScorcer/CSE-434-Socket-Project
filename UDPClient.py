from asyncio import Handle
from socket import *
from collections import OrderedDict
import pickle
import threading
import sys
#from turtle import update

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

ownLogicRing = []

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
			clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
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

				logicRings.pop(dropTarget)
				print("Removed the person you want to unfollow's logic ring from list of rings")
				print("Current rings: ")
				for ring in logicRings:
					print(ring)
			except ValueError:
				print('You are not following that person')
			except KeyError:
				print("You were not in that person's logical ring, so no change to logical rings currently in")
		elif userInput == "Tweet":
			tweet = input("Type your tweet: ")
			while len(tweet) > 140:
				tweet = input("Tweet too long. Try again. ")
			clientData.append(userHandle)
			clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
			serverData, serverAddress = clientSocket.recvfrom(2048)
			serverData = pickle.loads(serverData) #list of User objects that are following tweeter
			print("from server, received: ")
			for data in serverData:
				print(data.handle)
			#construct a follower ring if one hasn't been constructed yet
			if (userHandle not in logicRings):
				ownLogicRing = serverData
				print("Created new logic ring ")
				for ring in ownLogicRing:
					print(ring.handle)
			else :
				i = 0
				j = 0
			
				while (i < len(ownLogicRing)) or (j < len(serverData)):
					if ( i == len(ownLogicRing)):
						ownLogicRing.append(serverData[j])
						j = j+1
						i = i+1
					elif (j == len(serverData)):
						ownLogicRing.pop(i)
					elif ownLogicRing[i].handle < serverData[j].handle:
						ownLogicRing.pop(i)
					elif ownLogicRing[i].handle > serverData[j].handle:
						ownLogicRing.insert(i, serverData[j])
					elif (ownLogicRing[i].handle == serverData[j].handle):
						i = i+1
						j = j+1
				print("Updated logic ring to ")
				for ring in ownLogicRing:
					print(ring.handle)

			prev = 0
			after = 2
			for follower in ownLogicRing: 
					
				if follower.handle != userHandle:
					leftNeighbor = ownLogicRing[prev]
					#sets right neighbor as next user in list
					if after != len(ownLogicRing):
						rightNeighbor = ownLogicRing[after]
						after = after + 1
					#makes last follower's right neighbor the tweeter
					else:
						rightNeighbor = ownLogicRing[0]
						ownSetup = SetUp(userHandle, follower, ownLogicRing[1]) # tweeter, left neighbor, right neighbor
						clientSocket.sendto(pickle.dumps(ownSetup), listenAddress)
						
					prev = prev + 1
					setup = SetUp(userHandle, leftNeighbor, rightNeighbor)
					clientSocket.sendto(pickle.dumps(setup), ownLogicRing[prev].listenAddress)
		
			tweetMsg = Tweet(userHandle, tweet)
			if (len(ownLogicRing) > 1) :
				clientSocket.sendto(pickle.dumps(tweetMsg), ownLogicRing[1].listenAddress)	
				#sends exit request to server
			else :
				print("No followers to send tweets to")
				endTweet = []
				endTweet.append("End Tweet")
				clientSocket.sendto(pickle.dumps(endTweet), (serverIP, serverPort))
		elif userInput == "Exit":
						
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
		#remove users from client's following list and logic rings
		if type(receivedMsg) is Delete:
			following.remove(receivedMsg.delete)
			try:
				logicRings.pop(receivedMsg.delete)
				print("removed the logic ring related to deleted user")
			except KeyError:
				print("was not already in the deleted user's logical ring so no deletion of rings")
			
			print("\nfollowing is now", following)
			print("Type command: ")

		if type(receivedMsg) is SetUp:
			userNeighbors = Neighbors(receivedMsg.left, receivedMsg.right)
			logicRings.update({receivedMsg.sender: userNeighbors})
			print("Logic Ring added")
			print("Current logic rings you are apart of now:")
			for x in logicRings:
				print(x)
			print("Type command: ")

		if type(receivedMsg) is Tweet:
				
			global userHandle
			if receivedMsg.sender == userHandle:
				clientData = []
				clientData.append("End Tweet")
				listenSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
			else:
				print(receivedMsg.sender, f"sent a tweet by {logicRings[receivedMsg.sender].leftUser.handle} :", receivedMsg.tweet)	
				listenSocket.sendto(pickle.dumps(receivedMsg), logicRings[receivedMsg.sender].rightUser.listenAddress)
			print("Type command: ")
			
		
startListening = threading.Thread(target=listenChange, args=(), daemon=True)
startListening.start()
print("right is now listening")
cmdPort = threading.Thread(target=clientStart, args=())
print("starting cmd")
cmdPort.start()

cmdPort.join()
clientSocket.close()

print('client terminated')
