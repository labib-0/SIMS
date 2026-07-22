import hashlib
import base64

# Simple XOR encryption key for academic requirement (reversible encryption)
XOR_KEY = "SIMS_CAPSTONE_SECRET_KEY_2026"

def xor_crypt_string(data: str, key: str = XOR_KEY) -> str:
    """
    Applies XOR operation on string characters with a key.
    Running it twice with the same key encrypts and decrypts.
    """
    decrypted = []
    for i in range(len(data)):
        key_c = key[i % len(key)]
        decrypted_c = chr(ord(data[i]) ^ ord(key_c))
        decrypted.append(decrypted_c)
    return "".join(decrypted)

def encrypt_username(username: str) -> str:
    """
    Encrypts a username using XOR and Base64 encoding.
    """
    xored = xor_crypt_string(username)
    # Encode to base64 to store safely as string
    return base64.b64encode(xored.encode("utf-8")).decode("utf-8")

def decrypt_username(encrypted_username: str) -> str:
    """
    Decrypts a Base64 encoded XOR string back to the original username.
    """
    try:
        decoded_xored = base64.b64decode(encrypted_username.encode("utf-8")).decode("utf-8")
        return xor_crypt_string(decoded_xored)
    except Exception:
        return ""

def hash_password(password: str) -> str:
    """
    Hashes a password using SHA256.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain password matches the hashed one.
    """
    return hash_password(plain_password) == hashed_password
