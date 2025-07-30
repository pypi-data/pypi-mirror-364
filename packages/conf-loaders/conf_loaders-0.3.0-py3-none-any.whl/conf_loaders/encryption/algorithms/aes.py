import base64
from os import urandom

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .base import BaseEncryptor


class Encryptor(BaseEncryptor):

    label = 'aes'
    
    @classmethod
    def generate_salt(cls) -> str:
        """Generate salt"""
        random_bytes: bytes = urandom(16)
        return base64.b64encode(random_bytes).decode("utf-8")

    @classmethod
    def generate_secret(cls) -> str:
        """Return generated secret key in base64"""
        random_bytes: bytes = urandom(32)
        return base64.b64encode(random_bytes).decode("utf-8")

    @classmethod
    def encrypt(cls, plain_text: str, secret_key: str, salt: str) -> str:
        """Return encrypted string"""
        key: bytes = base64.decodebytes(secret_key.encode("utf-8"))
        iv: bytes = base64.b64decode(salt.encode("utf-8"))
        cipher = Cipher(algorithm=algorithms.AES(key), mode=modes.CBC(iv))
        encryptor = cipher.encryptor()
        # add PKCS7 padding
        plain_bytes = plain_text.encode('utf-8')
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plain_bytes) + padder.finalize()
        
        encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    @classmethod
    def decrypt(cls, ciphertext: str, secret_key: str, salt: str) -> str:
        """Return decrypted string"""
        key: bytes = base64.decodebytes(secret_key.encode("utf-8"))
        iv: bytes = base64.decodebytes(salt.encode("utf-8"))

        encrypted_data: bytes = base64.b64decode(ciphertext)

        # AES Decryption
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove PKCS7 padding
        padding_length = decrypted_data[-1]
        return decrypted_data[:-padding_length].decode('utf-8')

    @classmethod
    def test(cls):
        """
        >>> Encryptor.test() # doctest: +ELLIPSIS
        Original...
        """
        # Generate a secret key (32 bytes for AES-256) and an IV (salt, 16 bytes)
        secret_key = Encryptor.generate_secret()
        salt = Encryptor.generate_salt()  # IV must be 16 bytes for AES

        original_text = "Hello, AES encryption!"
        encrypted_text = Encryptor.encrypt(original_text, secret_key, salt)
        decrypted_text = Encryptor.decrypt(encrypted_text, secret_key, salt)

        print("Original text:", original_text)
        print("Encrypted text:", encrypted_text)
        print("Decrypted text:", decrypted_text)

        # Verify that decryption returns the original text
        assert original_text == decrypted_text, "Decrypted text does not match the original"
        print("Test passed: Decrypted text matches the original!")
