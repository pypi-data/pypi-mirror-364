from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64


def gen_keypair():
    priv_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    pub_key = priv_key.public_key()
    return (priv_key, pub_key)

def encrypt(nachricht, pub_key):
    message = pub_key.encrypt(
        nachricht.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return message

def encrypt_base64(message, pub_key):
    ciphertext = encrypt(message, pub_key)
    return base64.b64encode(ciphertext).decode('utf-8')

def decrypt_base64(b64_message, priv_key):
    ciphertext = base64.b64decode(b64_message.encode('utf-8'))
    return decrypt(ciphertext, priv_key).decode('utf-8')

def serial(key):
    try:
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    except AttributeError:
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

def load_private(key:str):
    #if isinstance(key, bytes):
    #    key = key.decode('utf-8')
    priv_key = serialization.load_pem_private_key(
        key.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    return priv_key

def load_public(key):
    pub_key = load_pem_public_key(
        key.encode('utf-8'),
        backend=default_backend()
    )
    return pub_key

def sign(message, priv_key):
    if isinstance(message, str):
        message = message.encode()
    signature = priv_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify(message, signature, pub_key):
    if isinstance(signature, str):
        signature = signature.encode()
    if isinstance(message, str):
        message = message.encode()
    try:
        pub_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def decrypt(message, priv_key):
    if isinstance(message, str):
        message = message.encode()
    decrypted_message = priv_key.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message

# Example:
# priv_key, pub_key = generiere_rsa_schluesselpaar()
# message = encrypt("Geheime Nachricht", pub_key)
# print(f"Verschlüsselt: {message}")
# 
# decrypted_message = decrypt(message, priv_key)
# print(f"Entschlüsselt: {decrypted_message}")