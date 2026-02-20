import base64
import json
import sys
import requests
import math
from Crypto.Util.number import long_to_bytes


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



def main1(base_url):
    # We need to sign this message
    msg = b'You got a 12 because you are an excellent student! :)'
    # print("Message->bytes->int")
    msg_num = int.from_bytes(msg)
    # print(msg_num)
    factors_of_msg = factors(msg_num)
    factors_of_msg.remove(1)
    factors_of_msg.remove(msg_num)
    # print(f"factors of our message:\n{factors_of_msg}")

    # I can see 5 is a factor:
    factor = factors_of_msg.pop()
    a = factor
    b = msg_num // factor

    print(f"Valid factor: {a*b==msg_num}")

    a_bytes = a.to_bytes()
    b_bytes = b.to_bytes(length=len(msg))
    #print(f"a: {a_bytes}\nb:{b_bytes}")

    # m = a*b
    # sign(m) = sign(a)*sign(b)
    # get signed a and b
    resp_a = requests.get(f"{base_url}/sign_random_document_for_students/{a_bytes.hex()}/").text
    resp_b = requests.get(f"{base_url}/sign_random_document_for_students/{b_bytes.hex()}/").text
    print(f"Response for msg a: {resp_a}")
    print(f"Response for msg b: {resp_b}")
    resp_a = json.loads(resp_a)
    resp_b = json.loads(resp_b)

    # I need the public key (N) for multiplying together?
    pk = json.loads(requests.get(f"{base_url}/pk/").text)
    N = pk["N"]

    signature = (int(resp_a["signature"], 16)-N)*(int(resp_b["signature"],16)-N) % N
    c = json_to_cookie(json.dumps({'msg': msg.hex(), 'signature': long_to_bytes(signature).hex() }))

    resp = requests.get(f'{base_url}/quote/', cookies={'grade': c})
    print(resp.text)


# Procedure 2:
# 

def main2(base_url):
    target_msg = b'You got a 12 because you are an excellent student! :)'
    r = 2

    # 1. Get the Public Key
    pk = requests.get(f'{base_url}/pk/').json()
    N, e = pk['N'], pk['e']

    # 2. Blind the message: (m * r^e) mod N
    m = int.from_bytes(target_msg, 'big')
    m_blind = (m * pow(r, e, N)) % N

    # 3. Request signature for the blinded "random" hex string
    # We convert the int to hex for the URL
    blind_hex = hex(m_blind)[2:]
    response = requests.get(f'{base_url}/sign_random_document_for_students/{blind_hex}/').json()
    
    if "error" in response:
        print(f"Error from server: {response['error']}")
        return

    s_blind = int.from_bytes(bytes.fromhex(response["signature"]), 'big')

    # 4. Unblind: s = (s_blind * r^-1) mod N
    # pow(r, -1, N) 
    s = (s_blind * pow(r, -1, N)) % N

    # 5. Craft the cookie
    sig_bytes = s.to_bytes(math.ceil(N.bit_length() / 8), 'big')
    cookie_data = json.dumps({
        'msg': target_msg.hex(),
        'signature': sig_bytes.hex()
    })
    
    grade_cookie = json_to_cookie(cookie_data)

    # 6. Claim your prize!
    final_resp = requests.get(f'{base_url}/quote/', cookies={'grade': grade_cookie})
    print(final_resp.text)



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'usage: {sys.argv[0]} <base url>', file=sys.stderr)
        exit(1)
    main1(sys.argv[1])
    main2(sys.argv[1])

# m = a*b
# sign(m) = sign(a)*sign(b)
