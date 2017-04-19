import base64
import random
import string

from cryptography.fernet import Fernet, InvalidToken

def get_fernet_with_key(key):
    return Fernet(key)

def encrypt(f, msg):
    return f.encrypt(str(msg))

def decrypt(f, token):
    return f.decrypt(str(token))

def login(f, token):
    try:
        password = decrypt(f, token)
        return True, password
    except InvalidToken:
        return False, None

def generate_fernet_key(pin, salt=None):
    if salt is None:
        useSalt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
    else:
        useSalt = salt

    pre_key = pin + "_" + useSalt
    key = base64.urlsafe_b64encode(pre_key)

    if salt is None:
        return key, useSalt
    else:
        return key

class Fernet2:
    key = None

    def __init__(self, key):
        self.key = key

    def encrypt(self, msg):
        pass

    def decrypt(self, msg):
        pass