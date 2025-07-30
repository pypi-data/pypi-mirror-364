
from typing import Optional
from abc import ABC, abstractmethod


class BaseEncryptor(ABC):

    label = ''
    """this algorithm label, using in full encryption"""
    
    @classmethod
    @abstractmethod
    def generate_salt(cls) -> str:
        """Return storaged salt"""
        
    @classmethod
    @abstractmethod
    def generate_secret(cls) -> str:
        """Return generated secret key in base64"""
    
    @classmethod
    @abstractmethod
    def encrypt(cls, plain_text: str, secret_key: str, salt: str) -> str:
        """Return encrypted string"""
        
        
    @classmethod
    @abstractmethod
    def decrypt(cls, ciphertext: str, secret_key: str, salt: str) -> str:
        """Return decrypted string"""

    @classmethod
    def encrypt_full(cls, plain_text: str, secret_key: str, salt: Optional[str] = None, sep: str = '$') -> str:
        """
        encrypts plain text to full secret cipher with format ALGO$SALT$CIPHER
        Args:
            plain_text:
            secret_key:
            salt:
            sep:

        Returns:

        """

        salt = salt or cls.generate_salt()

        try:
            ciphertext = cls.encrypt(plain_text=plain_text, secret_key=secret_key, salt=salt)
        except Exception:
            raise ValueError("Invalid secret")

        return sep.join(
            (cls.label.upper(), salt, ciphertext)
        )

