import socket
import sys
import threading
log_enabled = True
# Retreive our current client IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
client_ip_address = s.getsockname()[0]
print("Client IP address " + client_ip_address)
s.close()
# TODO read server connection inforamtion from a configuration file (json format for example)
server_ip_address = "127.0.0.1"
server_port = 8080
file_transfert_udp_ports_start = 2000
file_transfert_udp_ports_end = 60000
# Gestion des threads
receive_thread_running = True
sending_thread_running = True

# ongoing used port for file transfert list
default_file_transfert_protocol = "UDP"
upd_ongoing_used_port = []

#choix du pseudo
nickname = input("Choose your nickname: ")
# Connecting To Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((server_ip_address, server_port))

file_nickname_sender = ""
# Listening to Server and Sending Nickname

def log(log_message):
    if log_enabled:
        print(log_message)

def get_available_udp_port():
    for port in range(file_transfert_udp_ports_start, file_transfert_udp_ports_end):
        if port not in upd_ongoing_used_port:
            return port
    return -1

def receive():
    global file_nickname_sender
    global receive_thread_running
    global sending_thread_running
    global upd_ongoing_used_port
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
                break
            elif liste_message[0].upper() == '/SENDFILE':
                #print("send file command received")

                print(liste_message)
                file_nickname_sender = liste_message[2]
                print("user " + file_nickname_sender + " asks to send " + liste_message[7] + " /ACCEPTFILE or /DENYFILE : ")
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            sending_thread_running = False
            receive_thread_running = False
            server.close()
            break

# Sending Messages or command To Server
def write():
    global sending_thread_running
    global receive_thread_running
    global default_file_transfert_protocol
    while sending_thread_running:
        try:
            user_input = input()
            liste_user_input = user_input.split(' ')
            log(liste_user_input)
            if user_input.startswith('/'):
                if user_input.upper() == "/QUIT":
                    quit()
                    break
                    # TODO: To reorder and simplify the code
                elif liste_user_input[0].upper() == "/SENDFILE":
                    if len(liste_user_input) != 3:
                        print("Wrong or missing parameters, usage: /SENDFILE <username> <file path>")
                    else:
                        send_to_server(liste_user_input[0] + " " + liste_user_input[1] + " " + client_ip_address + " " + liste_user_input[2])
                elif liste_user_input[0].upper() == "/ACCEPTFILE":
                    send_to_server(user_input + " " + client_ip_address + " " + str(get_available_udp_port()) + " " + default_file_transfert_protocol)
                else:
                    send_to_server(user_input)
            else:
                message = '{}: {}'.format(nickname, user_input)
                send_to_server(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            receive_thread_running = False
            sending_thread_running = False
            break

def quit():
    global sending_thread_running
    global receive_thread_running
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