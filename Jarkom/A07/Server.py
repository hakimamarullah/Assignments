#!/usr/bin/env python

import socket
import threading
from typing import Tuple

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from nacl.public import PrivateKey, SealedBox, PublicKey

SERVER_NAME = socket.gethostname()
SERVER_IP = "10.128.0.9"
SERVER_PORT = 3051
BUFFER_SIZE = 2048
BLOCK_SIZE = 32


def generate_asymmetric_key():
    private_key = PrivateKey.generate()
    file_out = open("PrivateKeyServer.pem", "wb")
    file_out.write(bytes(private_key))
    file_out.close()

    public_key = private_key.public_key
    file_out = open("PublicKeyServer.pem", "wb")
    file_out.write(bytes(public_key))
    file_out.close()


def generate_symmetric_key():
    sym_key = get_random_bytes(BLOCK_SIZE)
    file_out = open("SymmetricKeyServer.txt", "wb")
    file_out.write(sym_key)
    file_out.close()


def get_symmetric_object(key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher


def encrypt_with_symmetric(cipher, message):
    result = cipher.encrypt(pad(message.encode(), BLOCK_SIZE))
    return result


def encrypt_with_asymmetric(public_key, message):
    box = SealedBox(PublicKey(public_key))
    result = box.encrypt(message)
    return result


def decrypt_with_symmetric(cipher, message):
    result = unpad(cipher.decrypt(message), BLOCK_SIZE)
    return result


def decrypt_with_asymmetric(private_key, message):
    box = SealedBox(PrivateKey(private_key))
    result = box.decrypt(message)
    return result


def encode_utf8_before_send(message):
    return message.encode("UTF-8")


def decode_utf8_before_print(message):
    return message.decode("UTF-8")


# This method loads the key to the program or generate a new one if freshly started.
def setup(type="fresh"):
    if (type == "fresh"):
        generate_asymmetric_key()
        generate_symmetric_key()

    symmetric_key = open("SymmetricKeyServer.txt", "rb")
    symmetric_key = symmetric_key.read()
    privkey = open("PrivateKeyServer.pem", "rb")
    privkey = privkey.read()
    pubkey = open("PublicKeyServer.pem", "rb")
    pubkey = pubkey.read()
    symmetric_key_object = get_symmetric_object(symmetric_key)
    return symmetric_key, privkey, pubkey, symmetric_key_object


def socket_handler_symmetric(connection: socket.socket, address: Tuple[str, int]):
    print(f"Receive connection from {address}")

    # TODO Selesaikan method ini untuk mengirim pesan dengan symmetric encryption
    inbound_msg = connection.recv(BUFFER_SIZE)

    print(decode_utf8_before_print(inbound_msg))

    connection.send(encode_utf8_before_send("Halo juga client!"))

    inbound_msg = connection.recv(BUFFER_SIZE)
    key = connection.recv(BUFFER_SIZE)
    print(decode_utf8_before_print(inbound_msg))
    
    cipher = get_symmetric_object(key)
    encrypted = encrypt_with_symmetric(cipher, "Symmetric Key diterima")

    connection.send(encrypted)

    msg_from_client = connection.recv(BUFFER_SIZE)

    decrypted = decrypt_with_symmetric(cipher, msg_from_client)
    raw_msg = decode_utf8_before_print(decrypted)

    NPM = raw_msg.split()[2]

    encrypted = encrypt_with_symmetric(cipher, f"Terima pesan {NPM}")

    connection.send(encrypted)

    connection.close()


def socket_handler_asymmetric(connection: socket.socket, address: Tuple[str, int]):
    print(f"Receive connection from {address}")
    # change this to empty/fresh if you are running it first time
    symmetric_key, privkey, pubkey, symmetric_key_object = setup("rerun")

    inbound_msg = connection.recv(BUFFER_SIZE)
    print(decode_utf8_before_print(inbound_msg))

    connection.send(encode_utf8_before_send("Halo juga Instance Client!"))

    # GET client pubk
    client_pubk = connection.recv(BUFFER_SIZE)
    client_pubk = client_pubk
    print(f"CLIENT PUBLIC KEY:\n{client_pubk}")

    # Send pubk to client
    connection.send(pubkey)

    # Get symmetric key
    symmetric_key_client = connection.recv(BUFFER_SIZE)
    decrypted_sym_key = decrypt_with_asymmetric(privkey, symmetric_key_client)
    with open("SymmetricKeyServer.txt", "wb") as f:
        f.write(decrypted_sym_key)
    
    cipher = get_symmetric_object(decrypted_sym_key)
    encrypted = encrypt_with_symmetric(cipher, "Symmetric Key diterima")
    connection.send(encrypted)

    msg_from_client = connection.recv(BUFFER_SIZE)
    decrypted = decrypt_with_symmetric(cipher, msg_from_client)
    raw_msg = decode_utf8_before_print(decrypted)
    print(f"ENCRYPTED MESSAGE FROM CLIENT: {msg_from_client}")
    print(f"DECRYPTED MESSAGE FROM CLIENT: {raw_msg}")

    NPM = raw_msg.split()[2]
    encrypted = encrypt_with_symmetric(cipher, f"Terima pesan {NPM}")
    connection.send(encrypted)
    


    connection.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
        sc.bind((SERVER_NAME, SERVER_PORT))
        sc.listen(0)

        print("Multithreading Socket Server Program")
        print("Hit Ctrl+C to terminate the program")

        while True:
            connection, address = sc.accept()
            # ganti handler ke tipe socket yang sedang dikerjakan
            thread = threading.Thread(target=socket_handler_asymmetric, args=(connection, address))
            thread.start()


if __name__ == "__main__":
    main()