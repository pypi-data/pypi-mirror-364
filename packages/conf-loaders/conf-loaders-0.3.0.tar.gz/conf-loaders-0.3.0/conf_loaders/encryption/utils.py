
from typing import Optional

from pathlib import Path

from ..utils.docrender_utils.aliases import PathLike, T, V
from ..utils.docrender_utils.files import read_text

from .encryptor import decrypt_password, is_like_secret


def load_secret(path: PathLike, ignore_errors: bool = True) -> Optional[str]:
    """returns secret key or None on problems"""
    secret_key_file = Path(path)
    if not secret_key_file.exists():
        m = "Secret key file not found but is required!"
        if ignore_errors:
            print(m)
            return
        raise Exception(m)

    secret_key = read_text(secret_key_file)
    if not secret_key.strip():
        m = "Empty secret key!"
        if ignore_errors:
            print(m)
            return
        raise Exception(m)

    return secret_key


def decrypt_passwords(
    container: T,
    secret_key: str = '',
    secret_key_file: Optional[PathLike] = None,
    sep: str = "$"
) -> T:
    """
    decrypts encrypted string values in json-like object
    Args:
        container: json-like object or simple type instance
        secret_key:
        secret_key_file: path to secret key
        sep:

    Returns:
        same object with decrypted values

    Notes:
        - any and only one from secret_key/secret_key_file must be specified
        - will not change original object
        - for not json-like object will return itself without raising errors and performing transformations
        - will not check/load secret key if there is no real need
    """

    assert bool(secret_key) + bool(secret_key_file) == 1, 'secret_key or secret_key_file must be specified but not both'

    def decrypt(value: str) -> str:
        nonlocal secret_key
        if not secret_key:  # load key
            secret_key = load_secret(secret_key_file, ignore_errors=False)

        return decrypt_password(value, secret_key=secret_key, sep=sep)[0]

    def run(obj: V) -> V:
        if isinstance(obj, (list, tuple)):
            return [run(i) for i in obj]

        if isinstance(obj, dict):
            return {k: run(v) for k, v in obj.items()}

        if isinstance(obj, str) and obj and is_like_secret(obj):
            return decrypt(obj)

        return obj

    return run(container)


