import socket
import sys
import threading

# estion des threads
receive_thread_running = True
sending_thread_running = True
#choix du pseudo
nickname = input("Choose your nickname: ")
# Connecting To Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(('127.0.0.1', 8080))

file_nickname_sender = ""
# Listening to Server and Sending Nickname
def receive():
    global file_nickname_sender
    global receive_thread_running
    while receive_thread_running:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = server.recv(1024).decode('UTF8')
            liste_message = message.split(' ')
            #print(liste_message)
            #print(liste_message[0])
            if message == '/NICK':
                server.send(nickname.encode('UTF8'))
            elif message == "/QUIT":
                quit()
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
            server.close()
            break

# Sending Messages To Server
def write():
    global sending_thread_running
    while sending_thread_running :
        user_input = input('')
        liste_user_input = user_input.split(' ')
        print(liste_user_input)

        # if user_input.upper() == "/QUIT":
        #     quit()
        if user_input.startswith('/'):
            send_to_server(user_input)
        else:
            message = '{}: {}'.format(nickname, user_input)
            send_to_server(message)


def quit():
    sending_thread_running =False
    receive_thread_running = False


def send_to_server(message):
    server.send(message.encode('UTF8'))

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

write_thread.join()
receive_thread.join()
server.close()
sys.exit()