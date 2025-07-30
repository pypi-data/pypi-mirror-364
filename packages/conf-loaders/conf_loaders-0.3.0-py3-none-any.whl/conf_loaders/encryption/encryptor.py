
from typing import Literal, Dict, Tuple
from typing_extensions import TypeAlias

from importlib import import_module
from functools import lru_cache

from .algorithms.base import BaseEncryptor

ALGORITHM: TypeAlias = Literal["AES", "RSA"]


@lru_cache(maxsize=None)
def _get_secret_regex(sep: str = '$') -> str:
    """returns secret regex for gotten sep and available algorithms"""
    a = '|'.join(ALGORITHM.__args__)
    if sep in '.$?[({-':
        sep = rf"\{sep}"
    return rf"^({a}){sep}.+{sep}.+$"


def is_like_secret(password: str, sep: str = '$') -> bool:
    """checks whether the string seems like to be a secret"""
    import re
    return bool(re.match(_get_secret_regex(sep), password))


@lru_cache(maxsize=None)
def get_encryptor_class(alg: ALGORITHM) -> BaseEncryptor:
    """Returns encryptor class based on alg (alg=filename)"""
    try:
        module = import_module(
            name=BaseEncryptor.__module__.rsplit('.', maxsplit=1)[0] + '.' + alg.lower()
        )

        return getattr(module, "Encryptor")
    except (ImportError, AttributeError):
        raise ValueError(f"Invalid algorithm: {alg}, available: {ALGORITHM.__args__}")


def encrypt_password(password: str, alg: ALGORITHM, secret_key: str, sep: str = "$") -> str:
    """
    Make an encrypted string in defined format based on alg, secret key + generated secret key.
    Competitive with **load_passwords[varname] result
    Note: made for web only/test usage
    """
    encryptor = get_encryptor_class(alg)
    return encryptor.encrypt_full(plain_text=password, secret_key=secret_key, sep=sep)


def load_ciphertext(
    alg: ALGORITHM,
    ciphertext: str,
    secret_key: str,
    salt: str,
) -> str:
    """Decrypt ciphertext using provided attributes """
    encryptor = get_encryptor_class(alg=alg)
    decrypted_text = encryptor.decrypt(
        ciphertext=ciphertext, secret_key=secret_key, salt=salt
    )
    return decrypted_text


def decrypt_password(full_password: str, secret_key: str, sep: str = "$") -> Tuple[str, ALGORITHM]:
    """
    decrypts password string
    Args:
        full_password: password in format AES$...
        secret_key:
        sep:

    Returns:
        - decrypted string
        - using algorithm
    """

    algorithm: ALGORITHM
    try:
        assert is_like_secret(full_password, sep)
        algorithm, salt, ciphertext = full_password.split(sep, maxsplit=2)
        assert ciphertext and salt and algorithm in ALGORITHM.__args__
    except (ValueError, AssertionError):
        raise ValueError("Incorrect encrypted string format")

    try:
        return load_ciphertext(algorithm, ciphertext=ciphertext, secret_key=secret_key, salt=salt), algorithm
    except Exception:
        raise Exception("Incorrect secret key or param")


def load_passwords(
    passwords: Dict[str, str],
    secret_key: str,
    config: dict,
    nested_sep: str = ".",
    sep: str = "$"
) -> Dict[str, Dict[str, str]]:
    """
    Decode + replace variables with password type in original passed dict or indent dict.
    Also returns dict with originally encrypted params

    Args:
        passwords: dict { var route -> encrypted value}
        secret_key:
        config: collection of variables to be changed
        nested_sep: level sep for var route
        sep: fields sep for encrypted strings
    """
    assert nested_sep
    assert sep

    successful_decrypt = {}
    
    for varname, password in passwords.items():

        try:
            decrypted_text, algorithm = decrypt_password(password, secret_key=secret_key, sep=sep)
        except Exception as e:
            print('\t' + e.args[0] + f" for item '{varname}'")
            continue

        # from shared.utils.settings_update import update_data_element
        from ..utils.settings_update import update_data_element
        try:
            config = update_data_element(
                command=varname, arg=decrypted_text,
                data=config, ignore_errors=False, show_values_on_error=False
            )
        except Exception as e:
            print('\t' + e.args[0])
            continue
        
        # save successfully updated param
        successful_decrypt[varname] = {"alg": algorithm, "secret_key": secret_key}

    return successful_decrypt


