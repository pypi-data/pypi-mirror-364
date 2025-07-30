
from typing import Union

import os

# from lockfile import FileLock
from filelock import FileLock

from .aliases import PathLike
from .files import mkdir_of_file


def get_lock(path: PathLike, mode: int = 0o664, timeout: float = -1) -> FileLock:
    """returns lock object with necessary permissions"""

    if not isinstance(path, str):
        path = str(path)

    if not path.endswith('.lock'):
        path += '.lock'

    mkdir_of_file(path)

    return FileLock(path, mode=mode, timeout=timeout)



