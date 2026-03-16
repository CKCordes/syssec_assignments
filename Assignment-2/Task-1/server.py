import socket
import struct
from Crypto.Cipher import AES

KEY_PATH = "preshared_key.pem"
MAX_MSG_SIZE = 1024

def decrypt(encrypted_data):
    with open(KEY_PATH, 'rb') as f:
        key = f.read()
    nonce = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ct = encrypted_data[28:]

    aes = AES.new(key, AES.MODE_GCM, nonce=nonce)

    try:
        decrypted_msg = aes.decrypt_and_verify(ct, tag)
        return decrypted_msg.decode("utf-8")
    except Exception as e:
        print(f"Error encountered decryption message: {e}")
        return None

if __name__ == "__main__":
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # Receive the ICMP reply
    while True:
        try:
            response, _ = icmp_socket.recvfrom(MAX_MSG_SIZE)
            # IP header is the first 20 bytes
            raw_icmp = response[20:28]
            icmp_type, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', raw_icmp)
            payload = response[28:]

            msg = decrypt(payload)
            if msg:
                print(msg)
            else:
                print("Could not print message")
        except socket.error as e:
            print(e)
