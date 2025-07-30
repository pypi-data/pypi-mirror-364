
#region IMPORTS

from typing import Sequence, Literal, Optional, Dict, Any, Union, List, Iterable, Tuple

import os
import io
import shutil
from pathlib import Path
import contextlib

from .aliases import PathLike
from .system import IS_WINDOWS

#endregion


@contextlib.contextmanager
def umask_context(umask: int):
    """sets umask on operation and restores after"""
    old_umask = os.umask(umask)
    try:
        yield
    finally:
        os.umask(old_umask)


#region RM/TOUCH

def _mkdir(path: Path):
    with umask_context(0o002):
        path.mkdir(parents=True, exist_ok=True)


def mkparents(path: PathLike):
    """equals to mkdir -p $(dirname path)"""
    _mkdir(Path(path).parent)


def mkdir_of_file(file_path: PathLike):
    """
    для этого файла создаёт папку, в которой он должен лежать
    """
    mkparents(file_path)


def mkdir(path: PathLike):
    """mkdir with parents"""
    _mkdir(Path(path))


def touch(path: PathLike):
    """makes empty file, makes directories for this file automatically"""
    mkdir_of_file(path)
    Path(path).touch()


def rmdir(path: PathLike):
    """rm dir without errors"""
    shutil.rmtree(path, ignore_errors=True)


def copy_file(source: PathLike, dest: PathLike):
    """performs file copying with target directory auto creation"""
    if os.path.exists(dest) and os.path.samefile(source, dest):
        return
    mkdir_of_file(dest)
    shutil.copyfile(source, dest)


def move_file(source: PathLike, dest: PathLike):
    """performs file moving with target directory auto creation"""
    mkdir_of_file(dest)
    shutil.move(source, dest)


#endregion

#region READ/WRITE/PARSE/DUMP


def read_json(path: PathLike) -> Union[Dict[str, Any], List]:
    import orjson
    if str(path).endswith('.gz'):
        import gzip
        with gzip.GzipFile(str(path), 'rb') as f:
            r = f.read()
    else:
        r = Path(path).read_bytes()
    return orjson.loads(r)


def to_json_bytes(data: Union[Dict, List, Any]) -> bytes:
    import orjson
    return orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS)


def save_json(path: PathLike, data: Union[Dict, List, Any]):
    mkdir_of_file(path)
    Path(path).write_bytes(
        to_json_bytes(data)
    )

    # dump = json.dumps(
    #     data.asdict() if hasattr(data, 'asdict') else data,
    #     ensure_ascii=False,
    #     indent=2
    # )
    # result_tmp = str(path)
    # Path(result_tmp).write_bytes(dump.encode('utf-8', 'ignore'))


def write_json(path: PathLike, data: Union[Dict, List, Any]):
    save_json(path, data)


def write_text(result_path: PathLike, text: str, encoding: str = 'utf-8'):
    mkdir_of_file(result_path)
    result_tmp = str(result_path) + '.tmp'
    Path(result_tmp).write_text(text, encoding=encoding, errors='ignore')
    if os.path.exists(result_path):
        os.remove(result_path)
    Path(result_tmp).rename(result_path)


def read_text(result_path: PathLike, encoding: str = 'utf-8'):
    return Path(result_path).read_text(encoding=encoding, errors='ignore')


def write_pickle(result_path: PathLike, data: Any):
    mkdir_of_file(result_path)
    import pickle
    dump = pickle.dumps(data)  # , protocol=4)
    result_tmp = str(result_path) + '.tmp'
    Path(result_tmp).write_bytes(dump)
    if os.path.exists(result_path):
        os.remove(result_path)
    Path(result_tmp).rename(result_path)


def read_pickle(result_path: PathLike):
    import pickle
    data = pickle.loads(Path(result_path).read_bytes())
    return data


def dumps_yaml(dct: Dict[str, Any]):
    """
    converts dictionary to yaml format string

    >>> print(dumps_yaml(dict(a=1, b=2, c='abc', d={'a': [1, 2], 'b': (1, 2), 'c': {1: 1, 2: 2}})).strip())
    a: 1
    b: 2
    c: abc
    d:
      a:
      - 1
      - 2
      b: !!python/tuple
      - 1
      - 2
      c:
        1: 1
        2: 2
    """
    from ._yaml import yaml_dump
    return yaml_dump(dct)


def write_yaml(path: PathLike, data: Dict):
    """writes dict to yaml"""
    write_text(path, dumps_yaml(data))


def parse_yaml(
    source: Union[PathLike, io.StringIO]
) -> Dict[str, Any]:
    """
    reads dict from .yaml file or string io

    >>> dct = {'a': 1, 'b': [1, 2, 3], 'c': {0: 0, 1: 1}}
    >>> s = dumps_yaml(dct)
    >>> assert parse_yaml(io.StringIO(s)) == dct
    """
    from ._yaml import yaml_load
    if isinstance(source, (str, Path)):
        with open(source, 'r', encoding='utf-8') as f:
            file_configs = yaml_load(f)
    else:
        file_configs = yaml_load(source)
    return file_configs


def read_yaml(
    source: Union[PathLike, io.StringIO]
) -> Dict[str, Any]:
    return parse_yaml(source)

#endregion


#region LOOKS LIKE

def looks_like(file: PathLike, pattern: Union[str, Tuple[str, ...]]):
    return (
        file if isinstance(file, str) else str(file)
    ).lower().endswith(pattern)


def looks_like_pdf(file: PathLike) -> bool:
    """
    >>> looks_like_pdf('p')
    False
    >>> looks_like_pdf('p.pdf')
    True
    >>> looks_like_pdf('p.PDF')
    True

    """
    return looks_like(file, '.pdf')


def looks_like_json(file: PathLike):
    return looks_like(file, '.json')


def looks_like_doc(file: PathLike):
    return looks_like(file, ('.doc', '.docx', '.rtf'))


def looks_like_text(file: PathLike):
    return looks_like(file, ('.txt', '.text'))


def looks_like_tiff(file: PathLike):
    return looks_like(file, ('.tif', '.tiff'))


def looks_like_png(file: PathLike):
    return looks_like(file, '.png')


def looks_like_jpeg(file: PathLike):
    return looks_like(file, ('.jpg', '.jpeg'))


def is_pdf_file(fpath: PathLike):
    return looks_like_pdf(fpath) and os.path.isfile(fpath)


def is_doc_file(fpath: PathLike):
    return looks_like_doc(fpath) and os.path.isfile(fpath)


def is_json_file(fpath: PathLike):
    return looks_like_json(fpath) and os.path.isfile(fpath)


def is_tiff_file(fpath: PathLike):
    return looks_like_tiff(fpath) and os.path.exists(fpath)


def get_first_file_endswith(
    files: Iterable[PathLike],
    endswith: Union[str, Sequence[str]]
) -> Optional[PathLike]:
    """
    searches for the first file with required end (like extension but not mandatory)
    Args:
        files: sequence of files candidates (usually files in the directory)
        endswith: pattern for the file end (or sequence of valid patterns)

    Returns:
        found file or None if not found
    """
    if not isinstance(endswith, str):
        endswith = tuple(endswith)
    return next(
        (p for p in files if Path(p).name.endswith(endswith)),
        None
    )


#endregion

def isfile_casesensitive(path: PathLike) -> bool:
    """
    checks whether the file exists exactly with this name

    Notes:
        on Windows test.txt TEST.txt are same files for many operations
    """
    if not os.path.isfile(path):
        return False
    directory, filename = os.path.split(path)
    return filename in os.listdir(directory)

#region PATHS


def doc_name(fpath: PathLike):
    """
    само имя файла, без пути и без расширения
    """
    return Path(fpath).stem


def full_path(file: PathLike):
    """resolved abspath"""
    return str(Path(file).absolute().resolve())


_illegal_path_symbols = set('№#$%&+;<=>?^`{}')


def is_like_relative_path(string: str) -> bool:
    """
    checks if string is like relative path (but bot strict)

    >>> is_like_relative_path('asferefefwfw11221')
    False
    >>> is_like_relative_path('./dererew')
    True
    >>> is_like_relative_path('models/model1')
    True
    >>> is_like_relative_path('C:\\\\re')
    False
    """
    if any(s in _illegal_path_symbols for s in string):
        return False

    is_path = '/' in string
    if not is_path and IS_WINDOWS:
        is_path = '\\' in string

    if not is_path:
        return False

    if IS_WINDOWS:
        return not string[1] == ':'
    return not string.startswith('/') and ':' not in string


def resolve_relative(
    relative_path: str,
    paths_to_start: Optional[Sequence[str]] = None
):
    """
    resolves abs or relative path

    Args:
        relative_path: path to resolve
        paths_to_start: additional dirs to try to resolve

    Returns:
        resolved path
    """
    # check existence; if relative -- check if relative from curdir
    if not os.path.exists(relative_path):
        if not is_like_relative_path(relative_path):  # absolute path case
            raise FileNotFoundError(f"file on absolute path '{relative_path}' is not exists")

        if not paths_to_start:
            paths_to_start = []
        else:
            paths_to_start = list(paths_to_start)

        for start in paths_to_start:
            assert os.path.isdir(start), f"argument path {start} is not an existing dir"

            path_new = str(Path(start).resolve().joinpath(relative_path).resolve())
            if os.path.exists(path_new):
                resolved = path_new
                break
        else:
            raise FileNotFoundError(
                f"cannot resolve path '{relative_path}' for any CWD from {tuple([os.getcwd()] + paths_to_start)}"
            )

        print(f"path {relative_path} is resolved as {resolved}")
        return resolved

    return os.path.abspath(relative_path)


def set_unix_sep(path: PathLike) -> str:
    """replaces backslash with unix /"""
    return str(path).replace(os.sep, '/')


def get_relative_path(path: PathLike, relative_to: PathLike) -> str:
    """
    returns relative path as string in unix-style format

    >>> assert get_relative_path('./a/b/c', './a') == 'b/c'
    >>> assert get_relative_path('./a', './a/b/c') == '../..'
    """
    return set_unix_sep(os.path.relpath(path, relative_to))


def isin(path: PathLike, parent: PathLike) -> bool:
    """
    checks whether the path is in other path
    Args:
        path: path to file or directory
        parent: the path to check whether it is its parent

    Returns:

    >>> assert isin('a/b/c', 'a/b')
    >>> assert isin('a/b/c', 'a')
    >>> assert not isin('a/b/c', 't/b')
    """
    return not get_relative_path(path, parent).startswith('..')

#endregion

#region META

_scales = {
    'b': 1,
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024
}


def file_size(file: PathLike, scale: Literal['b', 'kb', 'mb', 'gb'] = 'b'):
    """file size"""
    return Path(file).stat().st_size / _scales[scale]


def check_file_is_open(fn: PathLike, prefix: str = ' '):
    import psutil
    p = psutil.Process()
    for f in p.open_files():
        # print(f)
        if f.path == fn:
            print('!', prefix, "File is open:", fn)
            return
    print('!', prefix, "File is closed:", fn)


def assert_files_existence(files: Union[PathLike, Sequence[PathLike]], nonempty: bool = True):
    """asserts whether all input files exist"""
    if not isinstance(files, (list, tuple)):
        files = [files]

    for use, func, message in (
        (True, os.path.isfile, "next files don't exist or are not files"),
        (nonempty, os.path.getsize, "next files exist but are empty")
    ):
        if not use:
            continue

        mask = [func(f) for f in files]
        if not all(mask):
            raise FileNotFoundError(
                f"{message} ({sum(mask)}/{len(mask)}):\n\t" +
                '\n\t'.join(str(p) for f, p in zip(mask, files) if not f)
            )

#endregion


def concat_text_files(inpaths: Sequence[PathLike], outpath: PathLike):
    mkdir_of_file(outpath)
    with open(outpath, 'wb') as wfd:
        for f in inpaths:
            with open(f, 'rb') as fd:
                shutil.copyfileobj(fd, wfd)
                wfd.write(b"\n")


def nl(
    text: Union[str, os.PathLike, Iterable[str]],
    starts: int = 1,
    delimiter: str = '\t',
    only_nonempty: bool = True,
    left_align: bool = False,
    filler: str = ' ',
    save_to: Optional[PathLike] = None,
) -> List[str]:
    """
    add lines numbers at the start of each string

    Args:
        text: string sequence or a path to file
        starts: the number of first string
        delimiter: the text to put between numbers and original strings
        only_nonempty: numerate only nonempty lines
        left_align: align numbers at left column part, not right
        filler: character to fill empty space in numbers
        save_to: file to save the result

    Returns:
        list of new lines

    >>> def _(*args, **kwargs):
    ...     _lines = nl(*args, **kwargs)
    ...     print(f'{chr(10)}'.join(_lines))  # 10 is \n

    >>> t = ['line 1', '  line 2', '', '', 'line 5']
    >>> _(t, delimiter='   ')
    1   line 1
    2     line 2
    <BLANKLINE>
    <BLANKLINE>
    3   line 5
    >>> _(t, only_nonempty=False, delimiter=' --', starts=0)
    0 --line 1
    1 --  line 2
    2 --
    3 --
    4 --line 5
    >>> t = list('123456789abcd')
    >>> _(t, only_nonempty=False, delimiter='<-->')
     1<-->1
     2<-->2
     3<-->3
     4<-->4
     5<-->5
     6<-->6
     7<-->7
     8<-->8
     9<-->9
    10<-->a
    11<-->b
    12<-->c
    13<-->d
    >>> _(t, only_nonempty=False, delimiter='<-->', filler='0')
    01<-->1
    02<-->2
    03<-->3
    04<-->4
    05<-->5
    06<-->6
    07<-->7
    08<-->8
    09<-->9
    10<-->a
    11<-->b
    12<-->c
    13<-->d
    >>> _(t, only_nonempty=False, delimiter='<-->', left_align=True)
    1 <-->1
    2 <-->2
    3 <-->3
    4 <-->4
    5 <-->5
    6 <-->6
    7 <-->7
    8 <-->8
    9 <-->9
    10<-->a
    11<-->b
    12<-->c
    13<-->d
    """

    assert filler

    if isinstance(text, (str, Path)):
        text = read_text(text).split('\n')

    lines: List[str] = text

    lines_count = (
        sum(bool(line.strip()) for line in lines)
        if only_nonempty
        else len(lines)
    )

    max_number_len = len(str(lines_count + starts))

    empty = ' ' * (max_number_len + len(delimiter))

    def _get_text(number: int, line: str):
        if only_nonempty and not line.strip():
            return empty

        n = str(number)
        if left_align:
            n = n.ljust(max_number_len, filler)
        else:
            n = n.rjust(max_number_len, filler)

        return n

    # result = [
    #     f"{_get_text(i, line)}{delimiter}{line}"
    #     for i, line in enumerate(lines, starts)
    # ]

    result = []
    k = starts
    for line in lines:
        if only_nonempty and not line.strip():
            result.append(empty + line)
        else:
            s = _get_text(k, line)
            k += 1
            result.append(
                s + delimiter + line
            )

    if save_to:
        mkdir_of_file(save_to)
        write_text(save_to, '\n'.join(result))

    return result







