import socket
import threading
cmd1 = "NICK"
#creaction de la socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Lisaison de la socket à un port d'écoute avec bind()
server.bind(("127.0.0.1",4000))

#Fixer la taille de la file d'attente
server.listen(4)

clients = []
usernames = []

#diffuser un message a tous les clients
def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            msg = client.recv(1024)
            # verification du prtocol RFC

            broadcast(msg)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f"{username} left the chat".encode("ascii"))
            usernames.remove(username)
            break

#recevoir les connections des clients
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send(cmd1.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        if username not in usernames:
            usernames.append(username)
            print("utilisateur accepter")
            print(clients)
            clients.append(client)
        else:
            print("user name already in use")




        # Print And Broadcast Nickname
        print("Nickname is {}".format(username))
        broadcast("{} joined!".format(username).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Listening...")
receive()