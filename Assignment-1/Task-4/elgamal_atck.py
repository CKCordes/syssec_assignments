import base64
import json
import sys
import requests
import math
from Crypto.Util.number import long_to_bytes

# BASE_URL = sys.argv[1]

def json_to_cookie(j: str) -> str:
    """Encode json data in a cookie-friendly way using base64."""
    # The JSON data is a string -> encode it into bytes
    json_as_bytes = j.encode()
    # base64-encode the bytes
    base64_as_bytes = base64.b64encode(json_as_bytes, altchars=b'-_')
    # b64encode returns bytes again, but we need a string -> decode it
    base64_as_str = base64_as_bytes.decode()
    return base64_as_str

from functools import reduce

def factors(n):
    return set(reduce(
        list.__add__,
        ([i, n//i] for i in range(1, 100) if n % i == 0)))


def main(base_url):

    # 1. Get params (p)
    params = json.loads(requests.get(f"{base_url}/params/").text)
    p = params["p"]

    # We need to sign this message
    msg_new = b'You got a 12 because you are an excellent student! :)'
    base_msg = b'You never figure out that' 
    
    # 2. Get encryption for the base_msg
    base_hex = base_msg.hex()
    resp = requests.get(f'{base_url}/encrypt_random_document_for_students/{base_hex}/').json()
    
    ct_bytes = bytes.fromhex(resp["ciphertext"])

    # c1 and c2 are concatenated. We want to get c2, as this is the part with the msg.
    c1 = ct_bytes[:len(ct_bytes)//2]
    c2 = ct_bytes[len(ct_bytes)//2:]

    # 3. Calculate the inverse function 
    # m_old * x = m_new mod p 
    # x = m_new * m_old^-1 mod p
    x = (int.from_bytes(msg_new, 'big') * pow(int.from_bytes(base_msg,'big'), -1, p)) % p

    # 4. Create the new ciphertext
    c2_new = (int.from_bytes(c2, 'big') * x) % p
    blocksize = math.ceil(p.bit_length() / 8)
    c2_new_bytes = c2_new.to_bytes(blocksize, 'big')
    ct_new_bytes = c1 + c2_new_bytes

    # 5. Craft cookie, and profit
    c = json_to_cookie(json.dumps({'msg': msg_new.hex(), 'ciphertext': ct_new_bytes.hex() }))
    resp = requests.get(f'{base_url}/quote/', cookies={'grade': c})

    # Will return a flag if the attack was successful, otherwise an error message
    flag = resp.text
    print(flag)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'usage: {sys.argv[0]} <base url>', file=sys.stderr)
        exit(1)
    main(sys.argv[1])
