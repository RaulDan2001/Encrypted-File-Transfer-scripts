from fileinput import filename
import os
import socket
import random
import string
from tkinter import filedialog
from Crypto import Cipher
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class Sender(object):
    def __init__(self):
        #generez cheia si un nounce
        self.__key = self.key_generation()
        self.__nounce = get_random_bytes(16)
        print(self.__key)
        self.__cipher = AES.new(self.__key, AES.MODE_EAX, self.__nounce)
        #instantiez un socket internet pe un protocol orientat pe conexiune
        self.client = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
        self.client.connect(("localhost", 9999))

        self.file_name = self.choose_file()
        self.file_size = os.path.getsize(self.file_name)
        with open(self.file_name, "rb") as f:
            data = f.read()

        self.encrypted = self.__cipher.encrypt(data)

        self.send_file()
        self.client.close()

    def key_generation(self):
        characters = string.ascii_letters + string.digits
        key = ''.join(random.choices(characters, k = 16))
        return key.encode()
    
    def choose_file(self):
        pass

    def send_file(self):
        self.client.send(self.__nounce)
        
        metadata = f"{os.path.basename(self.file_name)}|{self.file_size}"
        self.client.send(metadata.encode('utf-8'))
        self.client.send(b'<META_END>')
        
        #trimit fluxul criptat
        self.client.sendall(self.encrypted)
        
        self.client.send(b'<END>')

    def choose_file(self):
        file_name = filedialog.askopenfilename(
            title="Choose the file you want to send",
            filetypes=[("All files", "*.*")])
        return file_name

Sender()
