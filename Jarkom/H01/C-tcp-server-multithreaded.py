import socket
import threading
import time
from typing import Tuple

SERVER_NAME = socket.gethostname()
SERVER_PORT = 4321
BUFFER_SIZE = 1024
print(SERVER_NAME)

def logic(input: str):
    time.sleep(5)
    output_value = {}
    for char in input:
        if char in output_value.keys():
            output_value[char] += 1
        else:
            output_value[char] = 1
    return str(output_value)


def socket_handler(connection: socket.socket, address: Tuple[str, int]):
    print(f"Menerima koneksi dari {address}")

    input_value_bytes = connection.recv(BUFFER_SIZE)
    input_value = input_value_bytes.decode("UTF-8")

    print(f"Menerima input dari {address}: {input_value}")

    output_value = logic(input_value)
    output_value_bytes = output_value.encode("UTF-8")

    connection.send(output_value_bytes)
    connection.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
        sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sc.bind((SERVER_NAME, SERVER_PORT))
        sc.listen(0)

        print("Contoh Socket Server TCP Multithreaded")
        print("Tekan Ctrl/CMD+C untuk menghentikan program")

        while True:
            connection, address = sc.accept()

            thread_job = threading.Thread(
                target=socket_handler, args=(connection, address)
            )
            thread_job.start()


if __name__ == "__main__":
    main()
