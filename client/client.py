import socket
import sys
import threading

# Choosing Nickname

nickname = input("Choose your nickname: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8080))

file_nickname_sender = ""
# Listening to Server and Sending Nickname
def receive():
    global file_nickname_sender
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            liste_message = message.split(' ')
            #print(liste_message)
            #print(liste_message[0])
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif liste_message[0] == '/SENDFILE':

                #print("send file command received")
                print(liste_message)
                file_nickname_sender = liste_message[2]
                print("user " + file_nickname_sender + " asks to send " + liste_message[7] + " /ACCEPTFILE or /DENYFILE : ")

            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break


# Sending Messages To Server
def write():
    while True:
        user_input = input('')
        liste_user_input = user_input.split(' ')
        print(liste_user_input)

        if user_input == "/QUIT":
            quit()
        elif user_input == "/HELP":  # Partie Dahbia
            help()
        elif liste_user_input[0].upper() == "/SENDFILE":  # Partie Dahbia
            send_file(user_input)
        elif user_input == "/LIST":
            list()
        elif user_input.upper() == "/DENYFILE" or liste_user_input[0].upper() == '/DENYFILE':
            client.send(user_input.encode('ascii'))
        else:
            message = '{}: {}'.format(nickname, user_input)
            client.send(message.encode('ascii'))


def quit():
    client.close()
    sys.exit()


def list():
    client.send("list")
    liste = client.recv(1024)


# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()


######################################################################################################
##Partie Dahbia
#######################################################################################################

def help():
    client.send('/HELP'.encode('ascii'))


def send_file(message):
    client.send(message.encode('ascii'))

################################# fin partie dahbia
