from socket import *
serverIP = gethostbyname(gethostname()) #gethostbyname(gethostname()) used for localhost. For other uses put server IP
serverPort = 28000
clientSocket = socket(AF_INET, SOCK_DGRAM)

while(userInput != "exit"):
    clientSocket.sendto(userInput.encode(),(serverIP, serverPort))
    userInput = input("Type command: ")
    clientSocket.sendto(userInput.encode(),(serverIP, serverPort))
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    print(modifiedMessage.decode())
clientSocket.close()
