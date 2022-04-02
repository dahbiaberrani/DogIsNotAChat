import socket
import sys
import threading

# Choosing Nickname

nickname = input("Choose your nickname: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8080))


# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == '/SENDFILE':
                client.send(input('accepter de vous recevoir le fichier: ').encode('ascii'))
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
        m = input('')
        liste_user_message = m.split(' ')
        print(liste_user_message)

        if m == "/QUIT":
            quit()
        elif m == "/HELP":  # Partie Dahbia
            help()
        elif liste_user_message[0].upper() == "/SENDFILE":  # Partie Dahbia
            send_file(m)
        elif m == "/LIST":
            list()
        else:
            message = '{}: {}'.format(nickname, m)
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
