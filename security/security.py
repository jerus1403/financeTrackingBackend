import bcrypt

def hash_password(password):
    encoded_password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    decoded_hashed = hashed_password.decode('utf-8')
    return decoded_hashed