import base64

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

def generate_fernet_key(pin):
    salt = Fernet.generate_key()[:25]
    pre_key = pin + "_" + salt
    key = base64.urlsafe_b64encode(pre_key)
    return key