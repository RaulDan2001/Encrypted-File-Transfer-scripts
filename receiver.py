import socket
import tqdm
from Crypto.Cipher import AES

class Receiver:
    def __init__(self):
        # Initialize the server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", 9999))
        self.server.listen()
        print("Server is listening on localhost:9999...")

    def key_input(self):
        while True:
            keystring = input('Write the key for this file: ')
            key = keystring.encode()
            if len(key) == 16:
                return key
            else:
                print("Enter a key that has 16 characters!!!")

    def handle_client(self, client, addr):
        print(f"Connected to {addr}")
        key = self.key_input()
        
        # Step 1: Receive the nonce (16 bytes)
        nounce = client.recv(16)
        print(f"Received nonce: {nounce}")
        
        cipher = AES.new(key, AES.MODE_EAX, nounce)

        # Step 2: Receive metadata until `<META_END>` marker
        metadata = b""
        while b'<META_END>' not in metadata:
            metadata += client.recv(1024)

        metadata, remaining_data = metadata.split(b'<META_END>', 1)

        try:
            metadata_decoded = metadata.decode('utf-8')
            print(f"Received metadata: {metadata_decoded}")
        except UnicodeDecodeError as e:
            print(f"Metadata decoding error: {e}")
            return

        # Parse the metadata
        file_name, file_size = metadata_decoded.split('|')
        file_size = int(file_size)

        # Step 3: Start receiving encrypted content
        file_bytes = remaining_data
        progress_bar = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=file_size)

        while len(file_bytes) < file_size:
            chunk = client.recv(1024)
            if b'<END>' in chunk:
                file_bytes += chunk[:chunk.find(b'<END>')]
                break
            file_bytes += chunk
            progress_bar.update(len(chunk))

        progress_bar.close()

        # Step 4: Write decrypted file to disk
        with open(file_name, "wb") as file:
            file.write(cipher.decrypt(file_bytes))

        print(f"File {file_name} received and decrypted successfully.")

    def run(self):
        sem = True
        try:
            while sem == True:
                client, addr = self.server.accept()
                self.handle_client(client, addr)
                client.close()
                print("Waiting for the next connection...")
                a = input ("Would you like to close the server ?: y/n ")
                if a == "y" :
                    sem = False
        except KeyboardInterrupt:
            print("\nShutting down the server...")
        finally:
            self.server.close()

server = Receiver()
server.run()



