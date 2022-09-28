import socket

from typing import Tuple


def request_parser(request_message_raw: bytearray, source_address: Tuple[str, int]) -> str:
    # Put your request message decoding logic here.
    # This method return a str.
    # Anda boleh menambahkan helper fungsi/method sebanyak yang Anda butuhkan selama 
    # TIDAK MENGUBAH ATAUPUN MENGHAPUS SPEC (parameter dan return type) YANG DIMINTA.
    pass

def response_parser(response_mesage_raw: bytearray) -> str:
    # Put your request message decoding logic here.
    # This method return a str.
    # Anda boleh menambahkan helper fungsi/method sebanyak yang Anda butuhkan selama 
    # TIDAK MENGUBAH ATAUPUN MENGHAPUS  SPEC (parameter dan return type) YANG DIMINTA.
    pass

def main():
    # Put the rest of your program's logic here (socket etc.). 
    # Pastikan blok socket Anda berada pada fungsi ini.
    pass

# DO NOT ERASE THIS PART!
if __name__ == "__main__":
    main() 