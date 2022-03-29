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
        m = input('').upper()
        if m == "/QUIT":
            quit()
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
