import socket
import threading
cmd1 = "NICK"
def receive():
    while True:
        try:
            # Recevoir les messages du serveur
            message = client.recv(1024).decode('ascii')
            if message == cmd1:
                client.send(username.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("ERROR!")
            client.close()
            break

# Envoyer un message au serveur
def send():
    while True:
        message = '{}: {}'.format(username, input(''))
        client.send(message.encode('ascii'))

username = input("Choisir un username: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1",4000))

# Creation des thread pour l'attente et l'envoi de messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=send)
write_thread.start()