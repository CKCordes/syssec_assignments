import socket
import sys
import struct
import time
from Crypto.Cipher import AES
import secrets
import os

ICMP_TYPE = 47
ID = 0
MAX_MSG_SIZE = 1024
KEY_PATH = "preshared_key.pem"

def encrypt(message):
    key = ""
    if os.path.isfile(KEY_PATH):
        with open(KEY_PATH, 'rb') as f:
            key = f.read()
    else:
        key = secrets.token_bytes(32)
        with open(KEY_PATH, 'wb') as f:
            f.write(key)
    nonce = secrets.token_bytes(12)
    aes = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = aes.encrypt_and_digest(message)
    return nonce+tag+ct

def send_ping(dest_ip, plain_msg, seq_num=1):
    # Encrypt message
    msg = encrypt(plain_msg)
    # Using https://forums.raspberrypi.com/viewtopic.php?t=362742 as inspo
    # Create a raw socket
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    checksum = 0
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)
    icmp_packet = struct.pack('!BBHHH', ICMP_TYPE, 0, checksum, ID, seq_num) + msg

    # Calculate the ICMP checksum
    # We need an even number of byutes to compute.
    count_to = (len(icmp_packet)//2)*2
    i = 0
    while i < count_to:
        checksum += (icmp_packet[i] << 8) + icmp_packet[i + 1]
        i += 2
    # if there is a leftover byte
    if i < len(icmp_packet):
        checksum += (icmp_packet[i] << 8)

    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF

    icmp_packet = struct.pack('!BBHHH', ICMP_TYPE, 0, checksum, ID, seq_num) + msg

    # Send the ICMP packet
    icmp_socket.sendto(icmp_packet, (dest_ip, 0))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <ip>")
        exit(1)
    print("Write your convert message:")
    msg = input()
    bmsg = msg.encode("utf-8")
    # Max size for a IPv4 packet is 65535 B. 20+8 are used as headers
    # Resulting max msg size: 65507
    # Adjust the MAX_MSG_SIZE accordingly
    msg_chunks = [bmsg[i:i+MAX_MSG_SIZE] for i in range(0, len(bmsg), MAX_MSG_SIZE)]

    for i, msg in enumerate(msg_chunks):
        send_ping(sys.argv[1], msg, seq_num=i)
