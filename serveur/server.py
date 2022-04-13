import socket
import threading
import os

log_enabled = True
#Todo read server information from a configuration file
# Informations de connexion
host = '127.0.0.1'
port = 8080

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Dictionnaire des clients et leurs username, keys = username, value = client
clients = {}

# Dictionnaire des client et leurs adresses IPs pour l'utilisation peandant les trasferts de fichiers.
clients_ip_addresses_dictionary = {}
# Liste des clients connectés
connected_users = []

file_exchange_list = []
approved_file_exchange_list = []

message_private_list = []
approved_private_messaging_list = []

file_sender = ""
file_receiver = ""

# return username for any client
def get_username(myclient):
    for username, client in clients.items():
        if myclient == client:
            return username
    return "username doesn't exist"

# fonction pour les logs
def log(log_message):
    # TODO: log in file also
    if log_enabled:
        print(log_message)

# diffuser un message pour tout les clients
def broadcast(message):
    for client in clients.values():
        client.send(message)

# Envoie la liste de tout les clients
def liste(client):
    liste_clients = ""
    for cli in clients.values():
        if cli in connected_users:
            liste_clients += f"{get_username(cli)} - connected\n"
        else:
            liste_clients += f"{get_username(cli)} - afk \n"
    client.send(liste_clients.encode('UTF8'))


# Handling Messages From Clients
def handle(client):
    global file_sender
    global file_receiver
    global connected_users
    global clients
    global file_exchange_list
    global message_private_list
    global approved_private_messaging_list
    global approved_file_exchange_list
    global clients_ip_addresses_dictionary
    while True:

        try:
            message = client.recv(1024).decode('UTF8')
            liste_user_message = message.split(' ')
            log(liste_user_message)
            if message.upper() == "/LIST":
                liste(client)
            elif message.upper() == "/HELP":
                log("/HELP Requested")
                client.send(('HELP, QUIT, AFK, WAKE, LIST, NAME, PRIVATEMSG, ACCEPTPRIVATEMSG, DENYPRIVATEMSG, SENDFILE, ACCEPTFILE, DENYFILE').encode('UTF8'))
            elif message.upper() == "/QUIT":
                log("/Quit command received")
                client.send("+success: you are successfully logged out".encode("UTF8"))
                client.send("/QUIT".encode("UTF8"))
                close_client(client)
                broadcast("-‘username’ logged out")
                break

            elif liste_user_message[0].upper() == "/SENDFILE":
                log("send file received")
                if len(liste_user_message) != 4:
                    client.send("-fail 1: an argument is needed for this command".encode('UTF8'))
                elif liste_user_message[1] not in clients.keys():
                    log("user not found")
                    client.send(("-fail 110 : user " + liste_user_message[1] + " not found").encode('UTF8'))
                elif not os.path.exists(liste_user_message[3]):
                    log("file does not exist")
                    client.send("-fail 202 : path not found, canceling".encode('UTF8'))
                # elif liste_user_message[2] != host:
                #
                #     log("ip adress not found")
                #     client.send("fail 205 : ip address invalid or not found".encode('UTF8'))
                else:
                    clients_key_list = list(clients.keys())
                    log(clients_key_list)
                    clients_val_list = list(clients.values())
                    log(len(clients_val_list))
                    file_nickname_receiver = liste_user_message[1]

                    log("file receiver nickname: " + file_nickname_receiver)
                    file_client_receiver = clients[file_nickname_receiver]
                    log("file receiver client retreived")
                    file_nickname_sender = clients_key_list[clients_val_list.index(client)]
                    log("file sender nickname : " + file_nickname_sender)
                    # save sender client IP address
                    file_sender_ip_address = liste_user_message[2]
                    clients_ip_addresses_dictionary[file_nickname_sender] = file_sender_ip_address
                    file_client_receiver.send(("/SENDFILE user " + file_nickname_sender + " asks to send you " + liste_user_message[3] + " /ACCEPTFILE or /DENYFILE ?").encode('UTF8'))
                    client.send("+success: your request is sent successfully, waiting for 'otherUserName' to respond".encode('UTF8'))
                    file_exchange_list.append((file_nickname_sender, file_nickname_receiver))
                    log(file_exchange_list)
                    log("file sender = " + file_nickname_sender)
                    log("file receiver = " + file_nickname_receiver)
            elif message.upper() == "/DENYFILE" or liste_user_message[0].upper() == "/DENYFILE":
                log('denyfile received')
                clients_key_list = list(clients.keys())
                clients_val_list = list(clients.values())
                if len(liste_user_message) != 2:
                    log("Argument missing for /DENYFILE command")
                    client.send("-fail 1: an argument is needed for this command ".encode('UTF8'))

                elif (liste_user_message[1], clients_key_list[clients_val_list.index(client)]) not in file_exchange_list:
                    log("file sender from receiver = " + clients_key_list[clients_val_list.index(client)])
                    log("file sender stocked by server = " + liste_user_message[1])
                    log("no exchange with " + liste_user_message[1])
                    client.send(("-fail 301: you do not have a sendfile request  from " + liste_user_message[1]).encode('UTF8'))
                else:
                    log("file sender from receiver = " + liste_user_message[1])
                    log("file sender stocked by server = " + clients_key_list[clients_val_list.index(client)])
                    # remove file transfert in file_exchange list
                    file_exchange_list.remove((liste_user_message[1], clients_key_list[clients_val_list.index(client)]))
                    client.send("+success: the file has been successfully denied".encode('UTF8'))

            # TODO Code /ACCEPTFILE  start new dedicated socket and thread for file exchange
            elif liste_user_message[0].upper() == "/ACCEPTFILE":
                log("File transfert accepted received")
                if len(liste_user_message) != 5:
                    client.send("fail: an argument is needed for this command".encode('UTF8'))
                else:
                    # TODO: Start DEbug from here
                    clients_key_list = list(clients.keys())
                    clients_val_list = list(clients.values())
                    file_nickname_sender = liste_user_message[1]

                    log(" accepting file from user: " + file_nickname_sender)
                    file_client_sender = clients[file_nickname_sender]
                    log("file client sender retrieved")
                    file_nickname_receiver = clients_key_list[clients_val_list.index(client)]
                    log("file receiver nickname : " + file_nickname_receiver)
                    if (liste_user_message[1], clients_key_list[clients_val_list.index(client)]) not in file_exchange_list:
                        client.send(("-fail 301: you do not have a sendfile request  from " + liste_user_message[1]).encode('UTF8'))
                    else:
                        # save file receiver client IP address
                        file_receiver_ip_address = liste_user_message[2]
                        clients_ip_addresses_dictionary[file_nickname_receiver] = file_receiver_ip_address
                        file_client_sender.send(("/ACCEPTFILE " + file_nickname_receiver + " " + file_receiver_ip_address + " " + liste_user_message[3] + " " + liste_user_message[4]).encode('UTF8'))
                        # Todo : remove file transfert from waiting_file_acceptance_list and add it to aproved_file_exchange_list
                        approved_file_exchange_list.append((liste_user_message[1], clients_key_list[clients_val_list.index(client)]))
                        log("Approved file exchange list = " + str(approved_file_exchange_list))
                        file_exchange_list.remove((liste_user_message[1], clients_key_list[clients_val_list.index(client)]))


            elif message.upper() == "/PRIVATEMSG" or liste_user_message[0].upper() == "/PRIVATEMSG":
                log("privatemsg recieved")
                if len(liste_user_message) != 2:
                    log("missing argument for /PRIVATEMSG command")
                    client.send("-fail 1: an argument is needed for this command".encode('UTF8'))
                else:
                    clients_key_list = list(clients.keys())
                    log(clients_key_list)
                    clients_val_list = list(clients.values())
                    log(len(clients_val_list))
                    private_message_receiver_nickname = liste_user_message[1]
                    if private_message_receiver_nickname not in clients_key_list:
                        log(private_message_receiver_nickname + " destination client does not exist!")
                        client.send(("-fail 110: user " + private_message_receiver_nickname + " not found").encode("UTF8"))
                    else:
                        private_message_sender_nickname = clients_key_list[clients_val_list.index(client)]
                        private_message_receiver_client = clients[private_message_receiver_nickname]
                        log("private message initiator : " + private_message_sender_nickname)
                        log("private message destination : " + private_message_receiver_nickname)

                        if (private_message_sender_nickname, private_message_receiver_nickname) in message_private_list:
                            log("private message request already ongoing")
                            client.send("-fail 300:  you have already sent a request to this user".encode('UTF8'))
                        elif (private_message_sender_nickname, private_message_receiver_nickname) in approved_private_messaging_list:
                            log("private messaging already established")
                            client.send(("-fail 301: you are already in private mode with " + private_message_receiver_nickname).encode('UTF8'))
                        else:
                            message_private_list.append((private_message_sender_nickname, private_message_receiver_nickname))
                            log("private list messaging : \n " + str(message_private_list))
                            private_message_receiver_client.send(("You received a request from " + private_message_sender_nickname + " to private chat. /ACCEPTPRIVATEMESSAGE or /DENYPRIVATEMESSAGE ?").encode('UTF8'))
                            client.send(("+success: your request is sent successfully, waiting for user " + private_message_receiver_nickname + " to respond").encode('UTF8'))

            elif message.upper() == "/DENYPRIVATEMESSAGE" or liste_user_message[0].upper() == "/DENYPRIVATEMESSAGE":
                log('deny private messaging received')
                clients_key_list = list(clients.keys())
                clients_val_list = list(clients.values())
                if len(liste_user_message) != 2:
                    log("Argument missing for /DENYPRIVATEMESSAGE command")
                    client.send("-fail 1: an argument is needed for this command".encode('UTF8'))

                elif (liste_user_message[1], clients_key_list[clients_val_list.index(client)]) not in message_private_list:
                    log("private message stocked by server = " + clients_key_list[clients_val_list.index(client)])
                    log("private message from receiver = " + liste_user_message[1])
                    log("no exchange with " + liste_user_message[1])
                    client.send(("-fail 310: you do not have a request from  from " + liste_user_message[1]).encode("UTF8"))

                else:
                    log("private message from receiver = " + liste_user_message[1])
                    log("private message stocked by server = " + clients_key_list[clients_val_list.index(client)])
                    #  remove from waiting private messaging list
                    message_private_list.remove((liste_user_message[1], clients_key_list[clients_val_list.index(client)]))
                    log("waiting approval private messaging list = " + str(message_private_list))
                    client.send(("+success: you just refuse to chat with " + liste_user_message[1] + " in private mode").encode('UTF8'))

            elif message.upper() == "/ACCEPTPRIVATEMESSAGE " or liste_user_message[0].upper() == "/ACCEPTPRIVATEMESSAGE":
                log('accept private messaging received')
                clients_key_list = list(clients.keys())
                clients_val_list = list(clients.values())
                if len(liste_user_message) != 2:
                    log("Argument missing for /ACCEPTPRIVATEMESSAGE command")
                    client.send("-fail 1: an argument is needed for /ACCEPTPRIVATEMESSAGE command, usage: "
                                "/ACCEPTPRIVATEMESSAGE <username>".encode('UTF8'))

                elif (liste_user_message[1], clients_key_list[clients_val_list.index(client)]) not in message_private_list:
                    log("private message stocked by server = " + clients_key_list[clients_val_list.index(client)])
                    log("private message from receiver = " + liste_user_message[1])
                    log("no exchange with " + liste_user_message[1])
                    client.send(
                        ("-fail 310: you do not have a request from  from " + liste_user_message[1]).encode("UTF8"))
                else:
                    log("private message from receiver = " + liste_user_message[1])
                    log("private message stocked by server = " + clients_key_list[clients_val_list.index(client)])
                    # add to approved private messaging list and remove from waiting private messaging list
                    message_private_list.remove((liste_user_message[1], clients_key_list[clients_val_list.index(client)]))
                    log("waiting approval private messaging list = " + str(message_private_list))
                    approved_private_messaging_list.append((liste_user_message[1], clients_key_list[clients_val_list.index(client)]))
                    log("approved private messaging list = " + str(approved_private_messaging_list))
                    client.send(("+success: Welcome to a private chat with " + liste_user_message[1]).encode('UTF8'))
            elif liste_user_message[0].upper() == "/PM":
                log("Private Message received ")
                clients_key_list = list(clients.keys())
                clients_val_list = list(clients.values())
                if len(liste_user_message) != 3:
                    log("Argument missing for /PM command")
                    client.send("-fail 1: an argument is needed for this command".encode('UTF8'))
               # Destination client doesn't exist in connecetd clients
                elif liste_user_message[1] not in clients_key_list:

                    log("private message for : " + liste_user_message[1])
                    log(liste_user_message[1] + " doesn't exist")
                    client.send(("-fail 110: user " + liste_user_message[1] + " not found").encode("UTF8"))

                else:
                    private_message_receiver_nickname = liste_user_message[1]
                    private_message_sender_nickname = clients_key_list[clients_val_list.index(client)]
                    private_message_receiver_client = clients[private_message_receiver_nickname]
                    log("private message initiator : " + private_message_sender_nickname)
                    log("private message destination : " + private_message_receiver_nickname)
                   # No established private chat with destination client
                    if (private_message_sender_nickname, private_message_receiver_nickname) not in approved_private_messaging_list:
                        log("you don't have a private chat with this user")
                        client.send("-fail:302: you are not in a private chat with this user".encode('UTF8'))

                    else:
                        private_message_receiver_client.send(("/PM " + private_message_sender_nickname + " " + liste_user_message[2]).encode('UTF8'))
                        client.send(("+success: message successfully sent to " + private_message_receiver_nickname).encode('UTF8'))

            elif liste_user_message[0].upper() == "/NAME":
                log(len(liste_user_message))
                if len(liste_user_message) != 2:
                    client.send("-fail 1: an argument is needed for this command".encode('UTF8'))
                else:
                    old_user_name = get_username(client)
                    new_user_name = liste_user_message[1]
                    clients[new_user_name] = clients[old_user_name]
                    del clients[old_user_name]
                    client.send(f"NEW_USERNAME {new_user_name}".encode('UTF8'))
                    client.send(f"You have successfully been renamed to {new_user_name}\n".encode('UTF8'))
                    broadcast(f"user {old_user_name} is now {new_user_name}".encode('UTF8'))

            elif message == '/AFK':
                if client in connected_users:
                    connected_users.remove(client)
                    client.send("+success : you are now in afk state".encode("UTF8"))
                    broadcast(f"-{get_username(client)} is in AFK mode now".encode("UTF8"))
                else:
                    client.send("-fail: you are already in AFK mode".encode("UTF8"))
            elif message == '/WAKE':
                if client not in connected_users:
                    connected_users.append(client)
                    client.send("+success: you are no longer AFK".encode("UTF8"))
                    broadcast(f"-{get_username(client)} is no longer AFK".encode("UTF8"))
                else:
                    client.send("-fail: you are not in afk mode".encode("UTF8"))
            else:
                if client in connected_users:
                    mes = '{}: {}'.format(get_username(client), message).encode("UTF8")
                    broadcast(mes)
                else:
                    client.send("You are in AFK mode now, type /WAKE to send message".encode("UTF8"))
        except:
            log("Exception occurred in server")
            close_client(client)
            break
def close_client(client):
    global clients
    #TODO need to properly stop correpsponding thread
    # Removing And Closing Clients
    client.send("/QUIT".encode("UTF8"))
    key = get_username(client)
    del clients[key]
    broadcast('{} left!'.format(key).encode('UTF8'))


# Receiving / Listening Function
def receive():
    global connected_users
    global clients
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname

        client.send('/NICK'.encode('UTF8'))
        username = client.recv(1024).decode('UTF8')
        while username in clients.keys():
            client.send("user name already in use".encode("UTF8"))
            username = client.recv(1024).decode('UTF8')

        # Print And Broadcast Nickname
        print("Nickname is {}".format(username))
        broadcast(("{} joined!".format(username)).encode('UTF8'))
        client.send(("OK you are now connected to server as " + username).encode('UTF8'))
        clients[username] = client
        connected_users.append(client)
        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("server listening to client connect on port " + str(port))
receive()
