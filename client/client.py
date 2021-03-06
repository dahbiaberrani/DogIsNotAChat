import os
import socket
import sys
import threading
import time
import json

# Server parameters
# TODO read server connection inforamtion from a configuration file
with open("../settings/settings.json") as settings_json_file:
    settings_values = json.load(settings_json_file)
    server_ip_address = settings_values["serverIPAddress"]
    server_port = settings_values["serverConnexionPortNumber"]
    file_receive_folder = settings_values["receivedFilesDestinationFolder"]

log_enabled = True
# Retreive our server IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
client_ip_address = s.getsockname()[0]
print("Client IP address " + client_ip_address)
s.close()

file_transfert_udp_ports_start = 2000
file_transfert_udp_ports_end = 60000
# Gestion des threads
receive_thread_running = True
sending_thread_running = True

# ongoing used port for file transfert list
default_file_transfert_protocol = "UDP"
upd_ongoing_used_port = []
tcp_ongoing_used_port = []

# choix du pseudo
nickname = input("Choose your nickname: ")
# Connecting To Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((server_ip_address, server_port))

# TODO: to clean if not needed
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


def is_udp_port_available(port):
    return port not in upd_ongoing_used_port


def send_file_udp(receiver_ip_address, udp_port_number, file_name):
    log("in send file")
    log("filename = " + file_name)
    log("receiver_ip_address = " + receiver_ip_address)
    log("Port number = " + udp_port_number)
    udp_peer_to_peer_file_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log("file transfer socket opened in file sender")
    buffer_size = 1024
    address = (receiver_ip_address, int(udp_port_number))
    log(address)
    # udp_peer_to_peer_file_send_socket.sendto(str.encode(file_name), address)
    time.sleep(5)
    log("openning the file")
    file = open(file_name, "rb")
    data = file.read(buffer_size)
    i = 0
    while data:
        log("buffer num: " + str(i) + " data = " + str(data))
        i += 1
        if udp_peer_to_peer_file_send_socket.sendto(data, address):
            print("sending file")
            data = file.read(buffer_size)
    print("file sent")

    time.sleep(5)
    udp_peer_to_peer_file_send_socket.close()
    file.close()


def receive_file_udp(sender_ip_address, udp_port_number, file_name):
    log("in receiving file")
    log("sender_ip_address = " + sender_ip_address)
    log("Port number = " + udp_port_number)
    address = ("0.0.0.0", int(udp_port_number))
    log(address)
    udp_peer_to_peer_file_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log("socket opened")
    udp_peer_to_peer_file_receive_socket.bind(address)
    log("socket binded")
    buffer_size = 1024

    #data, addr = udp_peer_to_peer_file_receive_socket.recvfrom(buffer_size)
    # log(addr)
    # print("Received File:", str(data.strip()))
    print("Received File:", "received_file.txt")
    file = open("./" + file_receive_folder + "/" + file_name, 'wb')
    log("file opened in write mode")
    data, addr = udp_peer_to_peer_file_receive_socket.recvfrom(buffer_size)
    log(addr)
    try:
        i = 0
        while data:
            print("Receiving file")
            file.write(data)
            udp_peer_to_peer_file_receive_socket.settimeout(5)
            data, addr = udp_peer_to_peer_file_receive_socket.recvfrom(buffer_size)
            log("address = " + str(addr))
            log("buffer num: " + str(i))
            i += 1
    except socket.timeout:
        file.close()
        udp_peer_to_peer_file_receive_socket.close()
        print("File Downloaded")



def receive():
    global file_nickname_sender
    global receive_thread_running
    global sending_thread_running
    global upd_ongoing_used_port
    global tcp_ongoing_used_port
    while receive_thread_running:
        log("Rreceiving : " + str(receive_thread_running))
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = server.recv(1024).decode('UTF8')
            liste_message = message.split(' ')
            # log(liste_message)
            # log(liste_message[0])
            if message == '/NICK':
                server.send(nickname.encode('UTF8'))
            elif message.upper() == "/QUIT":
                log("/QUIT command confirmed from server")
                receive_thread_running = False
                # quit()
                # break
            elif liste_message[0].upper() == '/SENDFILE':
                log("send file command received")
                file_nickname_sender = liste_message[2]
                print("user " + file_nickname_sender + " asks to send " + liste_message[7] + " /ACCEPTFILE or /DENYFILE : ")
            elif liste_message[0].upper() == '/STARTFILETRANSFER':
                log("Start file transfer info received")
                # TODO: Start debug here
                proposed_destination_ip_address_port_protocol = (liste_message[1], liste_message[2], liste_message[3], liste_message[4], liste_message[5])
                log(proposed_destination_ip_address_port_protocol)
                file_transfer_ip_address = proposed_destination_ip_address_port_protocol[1]
                file_transfer_port = proposed_destination_ip_address_port_protocol[2]
                file_transfer_protocol = proposed_destination_ip_address_port_protocol[3]
                file_name = proposed_destination_ip_address_port_protocol[4]

                if file_transfer_protocol == "UDP":
                    log("using UDP port " + file_transfer_port + " to receive the file")
                    upd_ongoing_used_port.append(file_transfer_port)
                    file_receive_thread = threading.Thread(target=receive_file_udp, args=(file_transfer_ip_address, file_transfer_port, file_name))
                    file_receive_thread.start()

                elif file_transfer_protocol == "TCP":
                    log("using TCP port " + file_transfer_port + " to receive the file")
                    tcp_ongoing_used_port.append(file_transfer_port)
                    # TODO: start dedicated thread to receive the file using TCP protocol
                else:
                    log("unknown proposed file transfer protocol")
            elif liste_message[0].upper() == "/ACCEPTFILE":
                log("/ACCEPTFILE command received")
                # retrieve port number and file name
                file_receiver_nickname = liste_message[1]
                file_receiver_ip_address = liste_message[2]
                file_receiver_porposed_port = liste_message[3]
                file_receiver_proposed_protocol = liste_message[4]
                file_name = liste_message[5]

                # check if proposed port is available
                # TODO: check which protocol is being to be used, here we assume only UDP is used
                if not is_udp_port_available(int(file_receiver_porposed_port)):
                    log(file_receiver_porposed_port + " is not available on file sender side")
                else:
                    log("Proposed port number from file receiver is also available on sender side, starting file sending")
                    # open udp file transfer  socket
                    #TODO: move following function call to a dedicated thread to don't block other usage of the client during file transfer
                    file_send_thread = threading.Thread(target=send_file_udp, args=(file_receiver_ip_address, file_receiver_porposed_port, file_name))
                    file_send_thread.start()
                    # send_file_udp(file_receiver_ip_address, file_receiver_porposed_port, file_name)
                    send_to_server("/STARTFILETRANSFER " + file_receiver_nickname + " " + client_ip_address + " " + file_receiver_porposed_port + " " + file_receiver_proposed_protocol + " " + file_name)

            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            quit()
            break


# Sending Messages or command To Server
def write():
    global sending_thread_running
    global receive_thread_running
    global default_file_transfert_protocol
    while sending_thread_running:
        log("sending: " + str(sending_thread_running))
        try:
            user_input = input()
            liste_user_input = user_input.split(' ')
            # log(liste_user_input)
            if user_input.startswith('/'):
                if user_input.upper() == "/QUIT":
                    send_to_server("/QUIT")
                    sending_thread_running = False
                    # TODO: To reorder and simplify the code
                elif liste_user_input[0].upper() == "/SENDFILE":
                    if len(liste_user_input) != 3:
                        print("Wrong or missing parameters, usage: /SENDFILE <username> <file_name>")
                    else:
                        if not os.path.exists(liste_user_input[2]):
                            log("file does not exist, please choose another file")
                        else:
                            send_to_server(liste_user_input[0] + " " + liste_user_input[1] + " " + client_ip_address + " " + liste_user_input[2])
                elif liste_user_input[0].upper() == "/ACCEPTFILE":
                    if len(liste_user_input) != 3:
                        print("wrong or missing parameters usage: /ACCEPTFILE <sender_username>  <file_name>")
                    else:
                        # TODO: need to control parameters check if the file realy existe
                        port = get_available_udp_port()
                        file_name = liste_user_input[2]
                        # TODO: to move send_file_udp(client_ip_address, port, file_name)
                        send_to_server("/ACCEPTFILE " + liste_user_input[1] + " " + client_ip_address + " " + str(port) + " " + default_file_transfert_protocol + " " + file_name)

                else:
                    send_to_server(user_input)
            else:
                # message = '{}: {}'.format(nickname, user_input)
                send_to_server(user_input)
        except:
            # Close Connection When Error
            print("An error occured!")
            quit()
            break


def quit():
    global sending_thread_running
    global receive_thread_running
    sending_thread_running = False
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
print("Stopping Client")
server.close()
sys.exit()
