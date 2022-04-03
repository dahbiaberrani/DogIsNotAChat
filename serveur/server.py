import socket
import threading
import sys
import os

# Connection Data
host = '127.0.0.1'
port = 8080

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []


# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)


# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024).decode('ascii')
            liste_user_message = message.split(' ')
            print(liste_user_message)
            if message == "list":
                print("Ca marche")
            elif message == "/HELP":
                print("/HELP Requested")
                client.send(('HELP, QUIT, AFK, WAKE, LIST, NAME, PRIVATEMSG, ACCEPTPRIVATEMSG, DENYPRIVATEMSG, SENDFILE, ACCEPTFILE, DENYFILE').encode('ascii'))

            elif liste_user_message[0].upper() == "/SENDFILE":
                print("send file received")
                if len(liste_user_message) != 4:
                    client.send("-fail 1: an argument is needed for this command".encode('ascii'))
                elif liste_user_message[1] not in nicknames:
                    print("user not found")
                    client.send(("-fail 110 : user " + liste_user_message[1] + " not found").encode('ascii'))
                elif not os.path.exists(liste_user_message[3]):
                    print("file does not exist")
                    client.send("-fail 202 : path not found, canceling".encode('ascii'))
                elif liste_user_message[2] != host:
                    print("ip adress not found")
                    client.send("fail 205 : ip address invalid or not found".encode('ascii'))
                else:
                    file_client_receiver = clients[nicknames.index(liste_user_message[1])]
                    file_nickname_sender = nicknames[clients.index(client)]

                    file_client_receiver.send(("/SENDFILE user " + file_nickname_sender + " asks to send you " + liste_user_message[3] + " /ACCEPTFILE or /DENYFILE ?").encode('ascii'))
                    client.send("+success: your request is sent successfully, waiting for 'otherUserName' to respond".encode('ascii'))
            elif message.upper() == "/DENYFILE" or liste_user_message[0].upper() == "/DENYFILE":
                print('denyfile received')
                if len(liste_user_message) != 2:
                    client.send("-fail 1: an argument is needed for this command ".encode('ascii'))
                else:
                    client.send("+success the file has been successfully denied".encode('ascii'))
            else:
                broadcast(message.encode('ascii'))
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        if nickname not in nicknames:

            nicknames.append(nickname)
            clients.append(client)
        else:
            print("user name already in use")

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("server listening ...")
receive()

######################################################################################################
##Partie Dahbia
#######################################################################################################


################################# fin partie dahbia
