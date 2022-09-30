from socket import *
import pickle
from sre_constants import SUCCESS
import threading

# add commandline parameters to accept user selected ports
# add commandline parameters to accept user selected ports
# add commandline parameters to accept user selected ports

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
	def __init__(self, name, followingList):
		self.name = name
		self.followingList = followingList

following = [] #Lists of users that client user is foloowing

serverIP = gethostbyname(getfqdn()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientPort = 28001 # add commandline parameters to accept user selected ports
clientIP = gethostbyname(getfqdn())
clientAddr = (clientIP,clientPort)
clientSocket.bind(clientAddr)

listenSocket = socket(AF_INET, SOCK_DGRAM)
listenPort = 28002 # add commandline parameters to accept user selected ports
listenIP = gethostbyname(getfqdn())
listenAddr = (listenIP, listenPort)
listenSocket.bind(listenAddr)

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
		if (serverData.encode() == "Success"):
			print("Success")
			break
		#otherwise ask user again for handle
		userHandle = input("Handle Already Exists. Try Again. ")
	while True:
		clientData = []
		userInput = input("Type command: ")
		clientData.append(userInput)
		match userInput:
			#query the server for handles and returns list of handles currently on the server
			case "Query Handles":
				clientSocket.sendto(pickle.dumps(clientData), serverAddress)
				serverData, serverAddress = clientSocket.recvfrom(2048)
				serverData = pickle.loads(serverData)
				print("Total Users: ", serverData[0])
				userList = serverData[1]
				for x in userList:
					print(x.handle)
				break
			case "Follow":
				followTarget = input('Please type the name of the person you want to follow: ')
				clientData.append(Req(userHandle, followTarget))
				#tries to find the followTarget to be follow in clientSide following lists lists
				try:
					unique = following.index(followTarget)
				#if error, then followTarget doesn't exist in following list, therefore append and sort
				except ValueError:
					following.append(followTarget)
					following.sort()

				clientSocket.sendto(pickle.dump(clientData),(serverIP, serverPort))
				#waits for server response
				serverData, serverAddress = clientSocket.recvfrom(2048)
				if serverData.decode() == "SUCCESS":
					print(userHandle , ' is now following ', followTarget)
					print("New following list: ", following)
				else:
					print("User is already following: ", followTarget)
			case "Drop":
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
			case "Tweet":
				print("Functionallity not implemented yet")
			case "Exit":
				#sends exit request to server
				clientData.append(ExitCode(userHandle , following))
				clientSocket.sendto(pickle.dumps(clientData), (serverIP, serverPort))
				finalMsg, serverAddress = clientSocket.recvfrom(2048)
				print(finalMsg.decode())
				break
			case _:
				print("Invalid Command")
#2nd thread function to listen for when a user exits
def listening():
	while True:
		message, serverAddress = listenSocket.recvfrom(2048)
		deleteMsg = pickle.loads(message)
		print('server sent a msg to ', deleteMsg.follower, ' to go and delete ', deleteMsg.name, ' but not rlly tho bc this is going to just one port but at least the delete msg is correct')


clientSocket.close()
cmdPort = threading.Thread(target=clientStart, args=())
cmdPort.start()

listeningPort = threading.Thread(target=listening, args=(), daemon=True)
listeningPort.start()

cmdPort.join()
listenSocket.close()

print('client terminated')