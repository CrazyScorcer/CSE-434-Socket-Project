from http import server
from socket import *
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverIP = gethostbyname(gethostname()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
serverAddress = (serverIP,serverPort)
serverSocket.bind(serverAddress)
print('The server is ready to receive')
while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
