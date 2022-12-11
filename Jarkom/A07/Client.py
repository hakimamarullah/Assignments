#!/usr/bin/env python

import socket

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from nacl.public import PrivateKey, SealedBox, PublicKey

SERVER_IP = "10.128.0.9"
SERVER_PORT = 3051
BUFFER_SIZE = 2048
BLOCK_SIZE = 32


def generate_asymmetric_key():
    private_key = PrivateKey.generate()
    file_out = open("PrivateKeyClient.pem", "wb")
    file_out.write(bytes(private_key))
    file_out.close()

    public_key = private_key.public_key
    file_out = open("PublicKeyClient.pem", "wb")
    file_out.write(bytes(public_key))
    file_out.close()


def generate_symmetric_key():
    sym_key = get_random_bytes(BLOCK_SIZE)
    file_out = open("SymmetricKeyClient.txt", "wb")
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
    if type == "fresh":
        generate_asymmetric_key()
        generate_symmetric_key()

    symmetric_key = open("SymmetricKeyClient.txt", "rb")
    symmetric_key = symmetric_key.read()
    privkey = open("PrivateKeyClient.pem", "rb")
    privkey = privkey.read()
    pubkey = open("PublicKeyClient.pem", "rb")
    pubkey = pubkey.read()
    symmetric_key_object = get_symmetric_object(symmetric_key)
    return symmetric_key, privkey, pubkey, symmetric_key_object


def connect_symmetric():
    # change this to empty/fresh if you are running it first time
    symmetric_key, privkey, pubkey, symmetric_key_object = setup("fresh")
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect((SERVER_IP, SERVER_PORT))

    # Example of sending "Hello" to server socket
    sc.send(encode_utf8_before_send("Halo server!"))

    msg_from_server = sc.recv(BUFFER_SIZE)

    print(decode_utf8_before_print(msg_from_server))

    sc.send(encode_utf8_before_send("Ini Symmetric Keynya"))
    sc.send(symmetric_key)

    msg_from_server = sc.recv(BUFFER_SIZE)

    decrypted = decrypt_with_symmetric(symmetric_key_object, msg_from_server)
    print(decode_utf8_before_print(decrypted))

    encrypted = encrypt_with_symmetric(symmetric_key_object, "Testing pesan 1906293051")
    sc.send(encrypted)

    reply_from_server = sc.recv(BUFFER_SIZE)
    decrypted = decrypt_with_symmetric(symmetric_key_object, reply_from_server)
    print(decode_utf8_before_print(decrypted))

    sc.close()


def connect_asymmetric():
    # change this to empty/fresh if you are running it first time
    symmetric_key, privkey, pubkey, symmetric_key_object = setup("fresh")
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect((SERVER_IP, SERVER_PORT))

    # Example of sending "Hello" to server socket
    sc.send(encode_utf8_before_send("Halo Instance Server!"))

    reply_from_server = sc.recv(BUFFER_SIZE)
    print(decode_utf8_before_print(reply_from_server))

    #Send pubk to server
    sc.send(pubkey)

    # Get server pubk
    server_pubk = sc.recv(BUFFER_SIZE)
    server_pubk = server_pubk
    print(f"SERVER PUBLIC KEY:\n{server_pubk}")

    # Send encrypted symmetric_key to server
    encrypted_sym_key = encrypt_with_asymmetric(server_pubk, symmetric_key)
    sc.send(encrypted_sym_key)

    reply_from_server = sc.recv(BUFFER_SIZE)
    decrypted = decrypt_with_symmetric(symmetric_key_object, reply_from_server)
    print(decode_utf8_before_print(decrypted))

    encrypted = encrypt_with_symmetric(symmetric_key_object, "Testing pesan 1906293051")
    sc.send(encrypted)

    reply_from_server = sc.recv(BUFFER_SIZE)
    decrypted = decrypt_with_symmetric(symmetric_key_object, reply_from_server)
    print(f"ENCRYPTED MESSAGE FROM SERVER: {reply_from_server}")
    print(f"DECRYPTED MESSAGE FROM SERVER: {decode_utf8_before_print(decrypted)}")

    sc.close()


def main():
    print("Starting Client Program.")
    # ganti method connect ke encryption yang sedang dikerjakan
    connect_asymmetric()
    print("Connection closed")


if __name__ == "__main__":
    main()
