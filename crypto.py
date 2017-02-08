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