import base64
from os import urandom
from .base import BaseEncryptor
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class InvalidSaltError(Exception):
    """Exception raised when the provided salt does not match the original."""
    pass


class Encryptor(BaseEncryptor):

    label = 'rsa'

    @classmethod
    def generate_salt(cls) -> str:
        """Generate a random salt (32 bytes) and return it as a base64-encoded string."""
        random_bytes: bytes = urandom(32)
        return base64.b64encode(random_bytes).decode("utf-8")

    @classmethod
    def generate_secret(cls) -> str:
        """Generate and return a base64-encoded private key."""
        private_key: rsa.RSAPrivateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        return cls._make_secret_key(private_key)

    @classmethod
    def encrypt(cls, plain_text: str, secret_key: str, salt: str) -> str:
        """Encrypt plain_text with salt using the public key extracted from the secret key."""
        private_key = cls._get_private_key(secret_key)
        public_key = private_key.public_key()
        salted_text: str = f"{salt}:{plain_text}"
        encrypted_bytes = public_key.encrypt(
            salted_text.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    @classmethod
    def decrypt(cls, ciphertext: str, secret_key: str, salt: str) -> str:
        """Decrypt an RSA-encrypted string using the private key and validate the salt."""
        private_key = cls._get_private_key(secret_key)
        encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))

        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        salted_string = decrypted_bytes.decode('utf-8')
        extracted_salt, original_text = salted_string.split(":", maxsplit=1)
        if extracted_salt != salt:
            raise InvalidSaltError("Provided salt does not match the original salt")
        return original_text

    @classmethod
    def _make_secret_key(cls, private_key: rsa.RSAPrivateKey) -> str:
        """Convert a private key to a base64-encoded string."""
        private_bytes: bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        secret_key: str = base64.b64encode(private_bytes).decode('utf-8')
        return secret_key

    @classmethod
    def _get_private_key(cls, secret_key: str) -> rsa.RSAPrivateKey:
        """Extract and return the private key from a base64-encoded secret key."""
        private_bytes = base64.b64decode(secret_key.encode('utf-8'))
        private_key = serialization.load_pem_private_key(
            private_bytes,
            password=None
        )
        return private_key
    
    @classmethod
    def test(cls):
        """
        >>> Encryptor.test() # doctest: +ELLIPSIS
        Original...
        """
        secret_key = Encryptor.generate_secret()
        salt = Encryptor.generate_salt() 

        original_text = "Hello, RSA encryption!"
        encrypted_text = Encryptor.encrypt(original_text, secret_key, salt)
        decrypted_text = Encryptor.decrypt(encrypted_text, secret_key, salt)

        print("Original text:", original_text)
        print("Encrypted text:", encrypted_text)
        print("Decrypted text:", decrypted_text)

        # Verify that decryption returns the original text
        assert original_text == decrypted_text, "Decrypted text does not match the original"
        print("Test passed: Decrypted text matches the original!")
