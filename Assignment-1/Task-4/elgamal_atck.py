import base64
import json
import sys
import requests
import math
from Crypto.Util.number import long_to_bytes

BASE_URL = sys.argv[1]

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


def main():
    params = json.loads(requests.get(f"{BASE_URL}/params/").text)
    p = params["p"]

    # We need to sign this message
    msg_new = b'You got a 12 because you are an excellent student! :)'
    # Cookie for localhost:
    #cookie_old = 'eyJtc2ciOiAiNTk2Zjc1MjA2NzY1NzQyMDYxMjA2ZjZlNmM3OTIwNjc2NTc0MjA2MTIwMzcyMDY5NmUyMDUzNzk3Mzc0NjU2ZDczMjA1MzY1NjM3NTcyNjk3NDc5MmUyMDQ5MjA2MTZkMjA3NjY1NzI3OTIwNjQ2OTczNjE3MDcwNmY2OTZlNzQ2NTY0MjA2Mjc5MjA3OTZmNzUyZSIsICJjaXBoZXJ0ZXh0IjogImY4MjEzMjc5NmM4Njc5OWE5ZDU1NjE2NDVhODk1NGIyYTJjNTYzYTJlMThkNWJiODIwMTJhMDNlOGM5MGZkMTYzOTRlMDQwNWY3NzcxMjAxM2RmMzQ5YmNhZTA2ZTQ3OTRhMzVjYjM4MmQ4Y2Y5NTM4YjMyZWUxMzc0MTJjZmIzZjg3Y2E1ODRmZTcxYjViMmU1YzU0ZTllMzI5Y2U3M2YyNDUxZDY0NWFjYWU3ZTQ4MTEyN2U0YjYzNWRhMWRmMTczOThkYWVhNGYzZDEwZmY1MzY5ODBmMmU0ZjlkZmVhMTY0ZjA2MTlmMmIwNTE3NjAxNTU3MjM1NjVkY2I3NzhiMWZlNmYyMTRkMTZlOWYwOWQxMDYwYWQ4ODE4MDE2MzQ0YTQ1NWNlNTFhODhjZmNhOTMwODFkYWE4ZTg3ZDBiYmZmNzliMjljZTgzZWExMDczNTEyODI2M2IwZDEyMWM1OWRlM2E0YzQyMDIwYzRmNDI2YjIwMGY2NTBhZDgwNmQyYzYwYzYxMjU5ZTM1YTE5NDBiYzdmYjJlMDk5MjY4MjdhMDc5MDViOTY0ODdkODY2ZTg4Zjk4YTQ5ZjM3NWNlMmVkYzMyNjkzYjY5ZmFiYjFlZjA4ZTZmM2M1ZWEwNGVjYjdmNmQ5NzJiZjY1ZGNhMzdjMmEyZDEwYTBiMGE2MjI0MjE0MTkxYjMyZjc2MDZkY2IyOTY4ZmM3NjA1MDA2OTY0Y2MyMTUwYjA5YmJjYTZjMjk2OWQwMTFjNDg3N2RhYzQyYzg5ZDRmYzUzYjAzMDQ5NmVhZTg5ZDZiZTUyMzAzMDg2OGI5MzAwMGNhZGE5NDU4ZGFlZDVmNDdhYmRhMmEwOGUyZGQzNDZmOTg0MGU2ZjJhNWY1ZmI4MmRkYjAzZTcxM2JiMDE3YzhhNDQzYjk1NjdmMTI2YTYwMGViZTBjMjRkMGUzMWI2YzBiNzFkMjJkMGI2YTZmMjJlOWFhNDY4NWM1YjAxMDE0OWM2YTg5ZTlmNGViNjExZTQyYWEyN2MzYzYzOTllZjlhNTFlMmQ5NjQzMzY2MTlmZTFiODhiY2E0MDc4MzViYzNjMTk3YTI0MjhjZTU5N2RiNGJmOGE0YjU2NGMwMTE2ZTAwYzYxMDg3N2MyMTdmNmI5MDNlODQxMDk2ZmI2MjRhNTMyYzRjYjAyNTM5OTJkZTRmOTlmZmUyNWYwMWQ5ZWE5MjY0YTQ2ZWQ1ZjcxOTdjZWI1YTAzNzdlNWU5ODQwYTczMWY1MTBiNzNlNTY1ZDhhMmQ0NzRkODBhODliNjVmMjg1NGJkMGI4OThmMjY1MTJjMWQyNTYzNzU5ZDU0NmNiZDVkZDZkMzk3YTM2YzJlMGQifQ'

    cookie_old = 'eyJtc2ciOiAiNTk2Zjc1MjA2NzY1NzQyMDYxMjA2ZjZlNmM3OTIwNjc2NTc0MjA2MTIwMzQyMDY5NmUyMDUzNzk3Mzc0NjU2ZDczMjA1MzY1NjM3NTcyNjk3NDc5MmUyMDQ5MjA2MTZkMjA3NjY1NzI3OTIwNjQ2OTczNjE3MDcwNmY2OTZlNzQ2NTY0MjA2Mjc5MjA3OTZmNzUyZSIsICJjaXBoZXJ0ZXh0IjogIjYzOTk2NDcyNmU0MjZmNTllNmZhNTUxNWIwMzBhODViYzY2NmNhM2NiZDIxOWQ5MDdlZmNjYzU2M2EzNmY5N2E5ZThiMjllNjJmOTc4MjAwNmU0YjFiYmM1YmU0MzJjOTJiMGQ3NjEzMGUxMjc2ZTk0MDYxNjUyZDg4ZTFkY2Q5MjU3NDRkNzFlYzNiNTFmNzdlM2FmNDc4YmQyMGM5YzAzYjkxNTVhOTI1MjJjOGFlYWY2NWYwYzNlMTE0NzRmOGE2NTg3MGI1Y2Q1YjZjMTI4NmRjMjQwMTBkMjA5YjM0NTUzMTNkMGIxZTEzOTFlYWI2MGExNTJmNjdjNzRkZWNmMGFlZTE0MDFiMTBmMjlkZjlkNTM4YjFmMTI3NWNiZjI3NzgxODU2OTNhZDJjM2YzMTgyNzI1Mjc2MzhmODE5Zjg3Mzc3MWVlYmJjOTllYTU0Y2JiY2ZlZmUxMzAyZjcyMWFhNTEwMWYwMGZkMTZhMDI0NmRjZjdhOWQ2N2Q2MTFjMjA1MjEyYTQwODM5NmI1ZGRhZDIxNDk4NjliYzZiNWNmMTQzZDQ2Nzc4ZDRkMDRhODk5MDdmYTNjZGY4ZDljMWFmYjk0Njk4ODBjNTNmMzYzYjlmODkxODZkMTgwMWY5NmVjMGM4ZWE2YTZiMDhmMzhlMTgxMTNjNWQxMTQ4ZDVjYzNjM2Y1ZWUzODhlNTQyYWNkM2MxYTYwMDk3OWNhN2IzOWU2MmNlMzBiODg4ZmExMmI5YjdhYjE2YWIyMDY1YjhiZjI5MDQ2YjFhYWYyYzI2MjA1ZWQxN2EyNWM3NzUwOGE1Mjg5MzM5YzU5MGYwODRmZGNlNmQ0NzY3ODVhNDBiMDQxZGM4NDYyMTMwZGI2ZDFjZjFiZWQ3NWNmMWIyMGYwZTlkMjM1NDdlMGFjOGMzMmNhMzk2M2MwYWEzM2Y5NDdmMWM4ZmFkM2IxNGFiMzJlOTRmN2FjNGVlNjcwODU1NDQ4ZTQ3NmFkMmZhOWUyNGZkZWMzZWNjNDY3N2I5OWNlZmRmMmZmMGYzM2FjOGJmZDZkMWE5YWNkMmRiMzZjMGQyY2FkZjRiNDlkZDY0MDFhMDJkMDZkNTViYzk3MTM5NDMzMjQ0NTBhYTdmM2EzOTU4NTYwOTEwMTI3YWQzMWMyMjQxM2M0MWNiZmQ1MDFkMjRlZGYzMjEyYjZhZGRhYmI0ZmUyNzJmMzllMTRjODA3NGI1NmZkZDk5Zjk4NjY3ZmUwN2IwMzUyM2U2YjI3YTIwNTM1YWVmYTNlYTBkMzg1NmFhY2UyNTE3NzI4NzMyZjc4OTMxYzcyMTA5ZDI1ODJiNzQ4NWY3YTgyMDc3MjBkOTI0Y2I0NDc2NzcifQ'
    cookie_padded = cookie_old + '=' * (-len(cookie_old) % 4)
    cookie_json_str = base64.b64decode(cookie_padded, altchars=b'-_').decode()
    cookie_data = json.loads(cookie_json_str)
    print(f"Cookie data:\n{cookie_data}")

    msg_old = bytes.fromhex(cookie_data["msg"])
    print(f"Old message:\n{msg_old}")

    ct_hex = cookie_data["ciphertext"]
    ct_bytes = bytes.fromhex(ct_hex)
    # c1 and c2 are concatenated. We want to get c2, as this is the part with the msg
    # With high probability, both c1 and c2 are p long, so we can split it down the middle?
    c1 = ct_bytes[:len(ct_bytes)//2]
    c2 = ct_bytes[len(ct_bytes)//2:]
    print(f"Ciphertext c1:\n{c1}\nCiphertext c2:\n{c2}")

    # m_old * x = m_new mod p
    # x = m_new*m_old**-1 mod p
    x = (int.from_bytes(msg_new, 'big') * pow(int.from_bytes(msg_old,'big'), -1, p)) % p
    print(f"Unknown x found to be: {x}")
    # After that we can transform ciphertext:
    # c_new = c_old * x
    c2_new = (int.from_bytes(c2, 'big') * x) % p
    blocksize = math.ceil(p.bit_length() / 8)
    c2_new_bytes = c2_new.to_bytes(blocksize, 'big')
    ct_new_bytes = c1 + c2_new_bytes
    print(f"New ciphertext in bytes:\n{ct_new_bytes}")
    c = json_to_cookie(json.dumps({'msg': msg_new.hex(), 'ciphertext': ct_new_bytes.hex() }))
    resp = requests.get(f'{BASE_URL}/quote/', cookies={'grade': c})
    print(resp.text)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'usage: {sys.argv[0]} <base url>', file=sys.stderr)
        exit(1)
    main()
