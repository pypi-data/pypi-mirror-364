"""
Special syntax for updating objects through yaml files

TODO add next operations:
    remove (by value)
    pop (by key)
"""

from typing import List, MutableMapping, Any, Union, Dict, Type
from typing_extensions import TypeAlias

import re

#region ALIASES

VARIABLES: TypeAlias = MutableMapping[str, Any]
"""variables dictionary collection"""


VARIABLE_INNER: TypeAlias = Union[VARIABLES, List]
"""object inside variables dictionary"""

#endregion


#region UTILS

def _is_int(s: str) -> bool:
    return bool(re.match(r"^\-?\d+$", s))


def _check_type(value: Any, valid_types: Any, label: str):
    if not isinstance(value, valid_types):
        raise ValueError(f"{label} ({value}) has invalid type for the operation: {type(value)}, requires {valid_types}")


#region getattr/setattr

def _getattr(obj: VARIABLE_INNER, key: Any, default: Any = ...):
    """
    extracts field from the object

    >>> r = dict(a=1, b=2)
    >>> assert _getattr(r, 'a') == 1
    >>> assert _getattr(r, 'c') is ...

    >>> r = [1, 2]
    >>> assert _getattr(r, 1) == 2
    >>> assert _getattr(r, -1) == 2
    >>> assert _getattr(r, 10) is ...

    >>> class R:
    ...     pass
    >>> r = R(); r.a = 1; r.b = 2
    >>> assert _getattr(r, 'a') == 1
    >>> assert _getattr(r, 'c') is ...
    """
    try:
        return obj[key]
    except TypeError:  # not dict-like
        pass
    except (KeyError, IndexError):  # no key index or no index in list
        return default

    return getattr(obj, str(key), default)


def getattr_(obj: VARIABLE_INNER, key: Union[str, int], default: Any = ...):
    """
    extracts field from the object by str/int key

    >>> r = {'1': 1, 2: 2}
    >>> assert getattr_(r, '1') == 1
    >>> assert getattr_(r, 1) == 1
    >>> assert getattr_(r, 2) == 2
    >>> assert getattr_(r, '2') == 2

    >>> r = [1, 2]
    >>> assert getattr_(r, 1) == 2
    >>> assert getattr_(r, -1) == 2
    >>> assert getattr_(r, '-1') == 2

    >>> class R:
    ...     pass
    >>> r = R()
    >>> assert getattr_(r, '1') is ...
    """
    assert key
    if isinstance(key, int) or _is_int(key):  # try integer case
        v = _getattr(obj, int(key), default)
        if v is not default:
            return v
    return _getattr(obj, str(key), default)


def _setattr(obj: VARIABLE_INNER, key: Union[str, int], value: Any):
    """
    sets object attribute
    >>> d = {}
    >>> _setattr(d, 1, 2); _setattr(d, '2', 3); _setattr(d, 'q', 4)
    >>> d
    {1: 2, '2': 3, 'q': 4}

    >>> d = [1, 2]
    >>> _setattr(d, 1, 3); _setattr(d, -2, 2)
    >>> assert d == [2, 3]

    >>> class R:
    ...     pass
    >>> r = R(); _setattr(r, 1, 2)
    >>> assert getattr_(r, 1) == 2
    """
    if isinstance(key, int):
        try:
            obj[key] = value
            return
        except TypeError:
            pass

    key = str(key)
    try:
        obj[key] = value
    except TypeError:
        setattr(obj, key, value)


def setattr_(obj: VARIABLE_INNER, key: Union[str, int], value: Any):
    """
    >>> d = [1, 2]
    >>> setattr_(d, 1, 3); setattr_(d, '-2', 2)
    >>> assert d == [2, 3]
    """
    if isinstance(key, int) or _is_int(key):
        _setattr(obj, int(key), value)
        return
    _setattr(obj, key, value)

#endregion

#endregion


#region OPERATIONS

class AssignOperation:
    """
    base update operation class which performs usual assignment

    >>> d = {'a': [1, 2, 3], 'b': {'c': 'word'}}
    >>> def _(route: str, value: Any):
    ...     AssignOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> _('d', 1)
    >>> _('a.0', 0)
    >>> _('a.-1', '1')
    >>> _('b.c', 'new')
    >>> _('b.d', 'd')
    >>> err('b.c.d', 0)
    >>> err('x.y', 0)
    >>> _('x', {})
    >>> _('x.y', 0)
    >>> d
    {'a': [0, 2, '1'], 'b': {'c': 'new', 'd': 'd'}, 'd': 1, 'x': {'y': 0}}
    """

    label = ''

    var_required = False
    """whether the changing variable itself must be present"""

    @classmethod
    def get_view(cls, route: str, value: Any, show_value: bool = True) -> str:
        label = f"@{cls.label}" if cls.label else ''
        if not show_value:
            value = '***'
        return f"{route}{label}: {value}"

    @classmethod
    def update_value(cls, field_value: Any, value: Any):
        """
        update current field according to value (and operation of class)
        this method must be overridden in subclasses

        Args:
            field_value: field to be changed/updated
            value: value to perform updates

        Returns:
            Ellipsis if no field update is required otherwise some new field value
        """
        return value

    @classmethod
    def update_variable(
        cls,
        route: str,
        value: Any,
        variables: VARIABLES,
        level_sep: str = '.',
        show_value_on_err: bool = True
    ):

        parts = route.split(level_sep)
        if not parts or not all(parts):
            raise ValueError(f"unknown variable route: {route} ({cls.get_view(route, value, show_value_on_err)})")

        _variables = variables
        done = []
        while True:
            p, *parts = parts
            var = getattr_(_variables, p)
            if var is Ellipsis:  # not found
                if parts or cls.var_required:  # if there are levels further it is the last level but presence is required
                    raise ValueError(f"{p} variable not found ({cls.get_view(route, value, show_value_on_err)})")

            done.append(p)

            if not parts:  # latest level reached
                try:
                    v = cls.update_value(var, value)
                except ValueError as e:
                    message = f"{level_sep.join(done)}: {e.args[0]} ({cls.get_view(route, value, show_value_on_err)})"
                    raise ValueError(message)
                if v is not Ellipsis:
                    setattr_(_variables, p, v)
                return

            _variables = var
            if isinstance(_variables, (bool, int, float, str, bytes)):  # simple type
                raise ValueError(
                    f"{route} field not found ({cls.get_view(route, value, show_value_on_err)}) "
                    f"because {level_sep.join(done)} is {type(_variables)} (cannot go deeper)"
                )


class SetDefaultOperation(AssignOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': 'word'}}
    >>> def _(route: str, value: Any):
    ...     SetDefaultOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> _('d', 1)
    >>> _('a.0', 0)
    >>> _('a.-1', '1')
    >>> _('b.c', 'new')
    >>> _('b.d', 'd')
    >>> err('b.c.d', 0)
    >>> err('x.y', 0)
    >>> _('x', {})
    >>> _('x.y', 0)
    >>> d
    {'a': [1, 2, 3], 'b': {'c': 'word', 'd': 'd'}, 'd': 1, 'x': {'y': 0}}
    """
    label = 'setdefault'
    var_required = False

    @classmethod
    def update_value(cls, field_value: Any, value: Any):
        if field_value is Ellipsis:
            return value
        return field_value


class BindOperation(AssignOperation):
    """
    >>> _list = [1, 2, 3]
    >>> _dict = {'c': 'word'}
    >>> d = {'a': _list, 'b': _dict, 'c': _list}
    >>> def _(route: str, value: Any):
    ...     BindOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> _('a', [1, 2])
    >>> _('c', [-1, -2])
    >>> err('b.e', [1])
    >>> err('b.c', [2])
    >>> _('b', {'new': 1})
    >>> d
    {'a': [-1, -2], 'b': {'new': 1}, 'c': [-1, -2]}
    >>> assert d['c'] is _list
    >>> assert d['b'] is _dict
    """
    label = 'bind'

    @classmethod
    def update_value(cls, field_value: Any, value: Any):
        if field_value is Ellipsis:
            if cls.var_required:
                raise ValueError(f'no var {field_value}')
            else:
                _check_type(value, (list, dict), 'value')
                return value

        _check_type(field_value, (list, dict), 'field')
        _check_type(value, (list, dict), 'value')

        field_value.clear()
        if isinstance(field_value, list):
            field_value.extend(value)
        else:
            field_value.update(value)
        return field_value


class AppendOperation(AssignOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': []}}
    >>> def _(route: str, value: Any):
    ...     AppendOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> _('a', 4)
    >>> _('b.c', 5)
    >>> err('b', 1)
    >>> err('b.d', 1)
    >>> d
    {'a': [1, 2, 3, 4], 'b': {'c': [5]}}
    """

    label = 'append'
    var_required = True
    default_value_type = list

    @classmethod
    def _update_value_exactly(cls, field_value: list, value: Any) -> list:
        field_value.append(value)
        return field_value

    @classmethod
    def _update_value(cls, field_value: list, value: Any) -> list:
        if field_value is Ellipsis:
            if cls.var_required:
                raise ValueError("field value is not set")
            else:
                field_value = cls.default_value_type()

        _check_type(field_value, cls.default_value_type, 'field')
        return cls._update_value_exactly(field_value, value)

    @classmethod
    def update_value(cls, field_value: list, value: Any) -> list:
        # _check_type(value, list, 'value')
        return cls._update_value(field_value, value)


class TryAppendOperation(AppendOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': []}}
    >>> def _(route: str, value: Any):
    ...     TryAppendOperation.update_variable(route, value, d)
    >>> _('a', 4)
    >>> _('b.c', 5)
    >>> _('b.d', 1)
    >>> d
    {'a': [1, 2, 3, 4], 'b': {'c': [5], 'd': [1]}}
    """
    label = 'try-append'
    var_required = False


class ExtendOperation(AppendOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': []}}
    >>> def _(route: str, value: Any):
    ...     ExtendOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> _('a', [4])
    >>> err('b.c', 5)
    >>> _('b.c', [5, 6, 7])
    >>> err('b', 1)
    >>> err('b.d', 1)
    >>> d
    {'a': [1, 2, 3, 4], 'b': {'c': [5, 6, 7]}}
    """

    label = 'extend'
    var_required = True

    @classmethod
    def _update_value_exactly(cls, field_value: list, value: list) -> list:
        field_value.extend(value)
        return field_value

    @classmethod
    def update_value(cls, field_value: list, value: list) -> list:
        _check_type(value, list, 'value')
        return cls._update_value(field_value, value)


class TryExtendOperation(ExtendOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': []}}
    >>> def _(route: str, value: Any):
    ...     TryExtendOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> _('a', [4])
    >>> err('b.c', 5)
    >>> _('b.c', [5, 6, 7])
    >>> err('b', 1)
    >>> err('b.d', [1, 2])
    >>> d
    {'a': [1, 2, 3, 4], 'b': {'c': [5, 6, 7], 'd': [1, 2]}}
    """

    label = 'try-extend'
    var_required = False


class UpdateOperation(AppendOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': {}}}
    >>> def _(route: str, value: Any):
    ...     UpdateOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> err('a', [4])
    >>> err('b.c', 5)
    >>> _('b.c', {5: 6, 7: 8})
    >>> err('b', 1)
    >>> err('b.d', 1)
    >>> d
    {'a': [1, 2, 3], 'b': {'c': {5: 6, 7: 8}}}
    """

    label = 'update'
    var_required = True
    default_value_type = dict

    @classmethod
    def _update_value_exactly(cls, field_value: dict, value: dict) -> dict:
        field_value.update(value)
        return field_value

    @classmethod
    def update_value(cls, field_value: dict, value: dict) -> list:
        _check_type(value, dict, 'value')
        return cls._update_value(field_value, value)


class TryUpdateOperation(UpdateOperation):
    """
    >>> d = {'a': [1, 2, 3], 'b': {'c': {}}}
    >>> def _(route: str, value: Any):
    ...     TryUpdateOperation.update_variable(route, value, d)
    >>> def err(route: str, value: Any):
    ...     try:
    ...         _(route, value)
    ...     except ValueError:
    ...         pass
    >>> err('a', [4])
    >>> err('b.c', 5)
    >>> _('b.c', {5: 6, 7: 8})
    >>> err('b', 1)
    >>> _('b.d', {1: 2})
    >>> d
    {'a': [1, 2, 3], 'b': {'c': {5: 6, 7: 8}, 'd': {1: 2}}}
    """

    label = 'try-update'
    var_required = False


#endregion


label_to_operation: Dict[str, Type[AssignOperation]] = {
    c.label: c for c in (
        AssignOperation, SetDefaultOperation, BindOperation,
        AppendOperation, TryAppendOperation,
        ExtendOperation, TryExtendOperation,
        UpdateOperation, TryUpdateOperation
    )
}


def update_data_element(
    command: str,
    arg: Any,
    data: VARIABLES,
    show_values_on_error: bool = True,
    ignore_errors: bool = False,
) -> VARIABLES:
    """
    performs update command on existing data
    Args:
        command: key@operation string
        arg: command argument
        data: data to be updated
        show_values_on_error: whether to show values in error messages
        ignore_errors: whether to skip errors

    Returns:
        updated data

    Notes:
        updates data inplace
    """
    if '@' in command:  # extract command
        try:
            key, label = command.rsplit('@', maxsplit=1)
            assert label in label_to_operation, (label, label_to_operation.keys())
            assert key, command
            cls = label_to_operation[label]
        except Exception:
            if ignore_errors:
                return data
            raise
    else:  # assign
        key = command
        cls = AssignOperation

    try:
        cls.update_variable(
            route=key, value=arg,
            variables=data, show_value_on_err=show_values_on_error
        )
    except Exception:
        if ignore_errors:
            return data
        raise

    return data


def update_data(
    commands: Dict[str, Any],
    data: VARIABLES,
    show_values_on_error: bool = True,
    ignore_errors: bool = False
) -> VARIABLES:
    """
    performs update commands on existing data
    Args:
        commands: dict { key@operation -> value }
        data: data to be updated
        show_values_on_error: whether to show values in error messages
        ignore_errors: whether to skip errors

    Returns:
        updated data

    Notes:
        updates data inplace

    >>> class R: pass
    >>> r = R()
    >>> _list = [5, 6, 7]
    >>> r.x = {'a': 1, 'b': {'c': [1, 2], 'd': _list}}
    >>> r.y = 11
    >>> r.z = [0, 1, 2]
    >>> r.lst = _list
    >>> cmds = {
    ...     'u': 'u',
    ...     'y@setdefault': 0,
    ...     'lst@bind': [7, 6, 5],
    ...     'x.c@bind': [3],
    ...     'z@append': 4,
    ...     'z@extend': [5, 6],
    ...     'v@try-append': [-1],
    ...     'n@try-extend': [-1],
    ...     'x.b@update': {'new': 'key'}
    ... }
    >>> _ = update_data(cmds, r)
    >>> r.__dict__
    {'x': {'a': 1, 'b': {'c': [1, 2], 'd': [7, 6, 5], 'new': 'key'}, 'c': [3]}, 'y': 11, 'z': [0, 1, 2, 4, 5, 6], 'lst': [7, 6, 5], 'u': 'u', 'v': [[-1]], 'n': [-1]}
    """

    if not commands:
        return data

    for command, arg in commands.items():
        data = update_data_element(
            command, arg,
            data=data,
            show_values_on_error=show_values_on_error, ignore_errors=ignore_errors
        )

    return data





