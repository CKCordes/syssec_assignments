import base64
import json
import math
import secrets
import string
import random
from hashlib import sha256

def k_bit_random(k):
    return random.randrange(2**(k-1)+1, 2**k - 1)

def miller_rabin_test(pc, rounds):
    # Implementation with help from
    # https://gist.github.com/Ayrx/5884790

    if pc % 2 == 0:
        return False

    r, s = 0, pc - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(rounds):
        a = random.randrange(2, pc - 1)
        x = pow(a, s, pc)
        if x == 1 or x == pc - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, pc)
            if x == pc - 1:
                break
        else:
            return False
    return True

def get_prime(k):
    while True: 
        pc = k_bit_random(k)
        if miller_rabin_test(pc, 40): 
            return pc

def generate_key(k):
    # For generating i will use the textbook from Cryptology class, and the implementation 
    # of rabin miller test from
    # https://www.geeksforgeeks.org/dsa/how-to-generate-large-prime-numbers-for-rsa-algorithm/
    key = {}
    p = get_prime(k//2)
    q = get_prime(k//2)
    # Generate e
    e = 0
    while True:
        e = random.randrange(0, (p-1)*(q-1))
        if math.gcd(e, (p-1)*(q-1)) == 1:
            break

    key["p"] = p
    key["q"] = q
    key["n"] = p * q
    key["e"] = e
    key["d"] = pow(e, -1, (p-1)*(q-1))
    return key

from Crypto.Signature.pss import MGF1
from Crypto.Hash import SHA256
def sign(message, key):
    # Using:
    # https://datatracker.ietf.org/doc/html/rfc8017#section-9.1.1

    """Sign a message using our private key."""
    # modulus and private exponent
    N = key['n']
    d = key['d']
    
    # First hash using SHA256
    mHash = sha256(message.encode('utf-8'))
    print(f"Pure SHA256 hashed message: {mHash.hexdigest()}")
    # Salt length shall be 32 bytes:
    sLen = 32
    hLen = len(mHash.hexdigest())

    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=sLen))
    print(f"Salt: {salt}")
    padding = '0'*8
    Mprime = padding + mHash.hexdigest() + salt
    print(f"Mprime: {Mprime}")
    H = sha256(Mprime.encode('utf-8'))
    hLen = len(H.hexdigest())
    # Aner ikke hvad emLen skal være
    #PS ='0' #* emLen - sLen - hLen - 2
    DB = '01' + salt #tilføj PS i starten
    dbMask = MGF1(H.digest(), hLen-1, SHA256)
    maskedDB = int(DB, 16) ^ dbMask
    EM = maskedDB + H.hexdigest() + '\xbc'
    print(f"EM: {EM}")


def verify(message: bytes, signature: bytes):
    """Verify a signature using our public key."""
    # modulus and private exponent
    N = rsa_key['_n']
    e = rsa_key['_e']
    # interpret the bytes of the message and the signature as integers stored
    # in big-endian byte order
    m = int.from_bytes(message, 'big')
    s = int.from_bytes(signature, 'big')
    if not 0 <= m < N or not 0 <= s < N:
        raise ValueError('message or signature too large')
    # verify the signature
    mm = pow(s, e, N)
    return m == mm


if __name__ == "__main__":
    key = generate_key(1024)
    sign("hej", key)
    #print(key)

