import configparser
import socket
import threading
from _thread import *
from common.colors import bcolors
from tabulate import tabulate

RUNNING = True
connections_dict = {}
messages_counter = 0  # used for command identifier
config_obj = configparser.ConfigParser()
config_obj.read("common/configfile.ini")
socket_info = config_obj["configuration"]
ServerSideSocket = socket.socket()
host = str(socket_info["host"])
port = int(socket_info["port"])




def look_for():
    """
    accepts a connection request by a client, then adds client to connections
    dict and starts new thread
    """
    global connections_dict
    while RUNNING:
        try:
            Client, address = ServerSideSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            connections_dict[str(address[1])] = Client
            start_new_thread(multi_threaded_client, (Client,))
        except socket.error as e:
            pass


def multi_threaded_client(connection):
    """
    called for starting new thread, receives data using recv() func
    """
    connection.send(str.encode('Server is working:'))
    try:
        while RUNNING:
            data = connection.recv(2048)
            if not data:
                continue
            print(bcolors.CONNECTION_RESP + "Message from client: " + data.decode('utf-8') + bcolors.ENDC)
    except socket.error as e:
        pass



def print_term_of_use():
    """
    prints table with optional commands and their arguments if needed
    """
    data = [
        ["connections", "shows clients connections", "-"],
        ["send", 'sends command to clients',
         "<connection id> <type> <payload> <arg 1> ... <arg n>"],
        ["kill", "removes client connection", "<connection id>"],
        ["result", "shows command result", "<command id>"],
        ["exit", "", "-"]
    ]
    print(
        bcolors.SERVER_BLUE + "#### WELCOME! CHOOSE COMMAND FROM MENU ####" + bcolors.ENDC)
    print(tabulate(data, headers=[bcolors.BOLD + "Command Name", "Description",
                                  "Arguments" + bcolors.ENDC]))


def send_command(user_input, connection_id):
    """
    sends command according to user input from CLI
    """
    global messages_counter
    connection = connections_dict[connection_id]
    connection.sendall(str.encode(str(messages_counter) + " " + user_input))
    messages_counter += 1

def show_connections():
    """
    prints table of current servers connections
    """
    data = []
    for key, value in connections_dict.items():
        data.append([key, host + ":" + key])
    print(tabulate(data, headers=[bcolors.BOLD + "connection id",
                                  "address" + bcolors.ENDC]))

def kill_connection(connection_id):
    """
    removes connection according to a given connection id
    """
    connection = connections_dict[connection_id]
    connection.sendall(str.encode("kill"))
    del connections_dict[connection_id]

def menu():
    """
    gets users input and runs matching function
    """
    global RUNNING
    print_term_of_use()
    while True:
        user_input = input(bcolors.SERVER_BLUE + "server>" + bcolors.ENDC)
        input_parts = user_input.split()
        if len(input_parts) == 0:
            print("Illegal input.")
            print_term_of_use()
            continue
        if input_parts[0] == "connections":
            show_connections()
            continue
        if input_parts[0] == "send":
            send_command(user_input, input_parts[1])
            continue
        if input_parts[0] == "kill":
            kill_connection(input_parts[1])
            continue
        if input_parts[0] == "exit":
            RUNNING = False
            ServerSideSocket.close()
            break
        else:
            print("Illegal input.")
            print_term_of_use()


try:
    ServerSideSocket.bind((host, port))
    ServerSideSocket.listen(5)
    threading.Thread(target=look_for).start()
    threading.Thread(target=menu).start()
except socket.error as e:
    print(str(e))
