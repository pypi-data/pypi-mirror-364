
"""
useful aliases
"""

#region IMPORTS

from typing import (
    Tuple, Sequence,
    Optional, Union, TypeVar, Literal,
    Hashable, Mapping,
    TYPE_CHECKING
)
from typing_extensions import TypeAlias

import os

import logging


#endregion

PathLike: TypeAlias = Union[str, os.PathLike]

T = TypeVar('T')
V = TypeVar('V')
