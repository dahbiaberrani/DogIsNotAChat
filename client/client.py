import socket
import threading

username = input("Choisir un username: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1",4000))

def receive():
    while True:
        try:
            # Recevoir les messages du serveur
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(username.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("ERROR!")
            client.close()
            break

# Envoyer un message au serveur
def write():
    while True:
        message = '{}: {}'.format(username, input(''))
        client.send(message.encode('ascii'))

# Creation des thread pour l'attente et l'envoie de messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()