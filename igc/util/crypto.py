import base64
import random
import string
from Crypto.Cipher import AES

def get_fernet_with_key(key):
    return Fernet2(key)

def encrypt(f, msg):
    return f.encrypt(str(msg))

def decrypt(f, token):
    return f.decrypt(str(token))

def login(f, token):
    try:
        password = decrypt(f, token)
        return True, password
    except AssertionError:
        return False, None

def generate_fernet_key(pin, salt=None):
    if len(pin) != 6:
        raise ValueError("Pin must be 6 digits")

    if salt is None:
        useSalt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
    else:
        useSalt = salt

    key = pin + "_" + useSalt
    if salt is None:
        return key, useSalt
    else:
        return key

class Fernet2:
    key = None
    aes = None

    IV = "INSTANTGRADECHEK"

    def __init__(self, key):
        self.key = key
        self.aes = AES.new(key, AES.MODE_CFB, self.IV)

    def encrypt(self, msg):
        ciphertext = base64.urlsafe_b64encode(self.aes.encrypt(msg + "CHECK"))
        return ciphertext

    def decrypt(self, msg):
        plaintext = self.aes.decrypt(base64.urlsafe_b64decode(msg))
        if "CHECK" not in plaintext:
            raise AssertionError("Invalid key")
        else:
            return plaintext[:-5]

