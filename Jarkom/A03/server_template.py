import socket

from typing import Tuple
from struct import unpack

SERVER_IP = "10.128.0.8"
DNS_ASDOS = "34.101.92.60"
PORT_ASDOS = 5353
SERVER_PORT = 5353
BUFFER_SIZE = 2048

def getRequestHeader(message):
    header = {}
    flags = bin(unpack("!H", message[2:4])[0])[2:].zfill(16)
    header["id"] = unpack("!H", message[0:2])[0]
    header["flags"] = flags
    header["qdcount"] = unpack("!H", message[4:6])[0]
    header["nscount"] = unpack("!H", message[8:10])[0]
    header["ancount"] = unpack("!H", message[6:8])[0]
    header["arcount"] = unpack("!H", message[10:12])[0]
    header["qr"] = flags[0]; header["opcode"] = int(flags[1:5],2); header["aa"] = flags[5]; header["tc"] = flags[6]
    header["rd"] = flags[7]; header["ra"] = flags[8]; header["ad"] = flags[10]; header["cd"] = flags[11]; header["rcode"] = int(flags[12:],2)

    return header

def getQuestion(message):
    question = {}
    start = 12
    ends = message[start] + start
    qname  = ""

    while True:
        if message[ends+1] == 0:
            qname += message[start+1:ends+1].decode("utf-8")
            break
        qname += message[start+1:ends+1].decode("utf-8") + "."
        start = ends + 1
        ends = message[ends+1] + start

    startQtype = start + message[start] + 2
    startQclass = startQtype + 2
    question["qname"] = qname 
    question["qtype"] = unpack("!H", message[startQtype: startQtype + 2])[0]
    question["qclass"] = unpack("!H", message[startQclass : startQclass + 2])[0]
    
    return question

def request_parser(request_message_raw: bytearray, source_address: Tuple[str, int]) -> str:
    header = getRequestHeader(request_message_raw)
    question = getQuestion(request_message_raw)
    output = [
        "="*73,
        f'[Request from ({source_address[0]}, {source_address[1]})]',
        "-"*73,
        "HEADERS",
        f'Request ID: {header["id"]}',
        f'QR: {header["qr"]} | OPCODE: {header["opcode"]} | AA: {header["aa"]} | TC: {header["tc"]} | RD: {header["rd"]} | RA: {header["ra"]} | AD: {header["ad"]} | CD: {header["cd"]} | RCODE: {header["rcode"]}',
        f'Question Count: {header["qdcount"]} | Answer Count: {header["ancount"]} | Authority Count: {header["nscount"]} | Additional Count: {header["arcount"]}',
        "-"*73,
        "QUESTION",
        f'Domain Name: {question["qname"]} | QTYPE: {question["qtype"]} | QCLASS: {question["qclass"]}',
        "-"*73
    
    ]
    return "\n".join(output)





def response_parser(response_mesage_raw: bytearray) -> str:
    # Put your request message decoding logic here.
    # This method return a str.
    # Anda boleh menambahkan helper fungsi/method sebanyak yang Anda butuhkan selama 
    # TIDAK MENGUBAH ATAUPUN MENGHAPUS  SPEC (parameter dan return type) YANG DIMINTA.
    pass


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sc:
        sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sc.bind((SERVER_IP, SERVER_PORT))

       

        dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while True:
            inbound_message_raw, source_addr = sc.recvfrom(BUFFER_SIZE)
            print(request_parser(inbound_message_raw, source_addr))
  
            outgoing_message_raw = inbound_message_raw

            dns.sendto(outgoing_message_raw, (DNS_ASDOS, PORT_ASDOS))
           
            inbound_message_raw_dns, source_addr_dns = dns.recvfrom(BUFFER_SIZE)
    
            sc.sendto(inbound_message_raw_dns, source_addr)
    dns.close()

# DO NOT ERASE THIS PART!
if __name__ == "__main__":
    main()
   