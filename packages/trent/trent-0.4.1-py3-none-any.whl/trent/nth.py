from typing import Any, Iterable, Optional, Sequence, Tuple, TypeVar, overload

# ---------------------

_T = TypeVar('_T')
_T2 = TypeVar('_T2')


class MissingValueException(Exception):
    def __init__(self, val, fn_name: str) -> None:
        self._value = val
        self._fn_name = fn_name
    
    def __str__(self) -> str:
        return f'Missing {self._fn_name} for value: {self._value}'


class __no_value():
    def __init__(self) -> None:
        pass


def _nth(coll:Optional[Iterable[_T]], n:int, position_name, default:_T2 = None) -> _T|_T2:
    if (isinstance(coll, Sequence)):
        if len(coll) > n:
            return coll[n]
        return default
    if isinstance(coll, Iterable):
        it = iter(coll)
        i = 0
        while i < n:
            try:
                next(it)
            except StopIteration:
                return default
            i += 1
        try:
            return next(it)
        except StopIteration:
            return default
    if coll is None:
        return default
    raise Exception("Cant get '{}' attribute from value: {}.\n It is not a Collection|None".format(position_name, coll))


# ===========================================================================

# --------------------------
#       FIRST

@overload
def first(coll: Tuple[_T]) -> Optional[_T]: ...
@overload
def first(coll: Tuple[_T, Any]) -> Optional[_T]: ...
@overload
def first(coll: Tuple[_T, Any, Any]) -> Optional[_T]: ...
@overload
def first(coll: Tuple[_T, Any, Any, Any]) -> Optional[_T]: ...
@overload
def first(coll: Tuple[_T, Any, Any, Any, Any]) -> Optional[_T]: ...
@overload
def first(coll: Tuple[_T, Any, Any, Any, Any, Any]) -> Optional[_T]: ...
@overload
def first(coll: Tuple[_T, Any, Any, Any, Any, Any, Any]) -> Optional[_T]: ...
@overload
def first(coll: Iterable[_T]|Any) -> Optional[_T]: ...

def first(coll: Iterable):
    return _nth(coll, 0, 'first')


# ------------------------------
#       SECOND

@overload
def second(coll: Tuple[Any, _T]) -> Optional[_T]: ...
@overload
def second(coll: Tuple[Any, _T, Any]) -> Optional[_T]: ...
@overload
def second(coll: Tuple[Any, _T, Any, Any]) -> Optional[_T]: ...
@overload
def second(coll: Tuple[Any, _T, Any, Any, Any]) -> Optional[_T]: ...
@overload
def second(coll: Tuple[Any, _T, Any, Any, Any, Any]) -> Optional[_T]: ...
@overload
def second(coll: Tuple[Any, _T, Any, Any, Any, Any, Any]) -> Optional[_T]: ...
@overload
def second(coll: Iterable[_T]|Any) -> Optional[_T]: ...

def second(coll: Iterable[_T]|Any) -> Optional[_T]:
    return _nth(coll, 1, 'second')


# -------------------------------
#       THIRD

@overload
def third(coll: Tuple[Any, Any, _T]) -> Optional[_T]: ...
@overload
def third(coll: Tuple[Any, Any, _T, Any]) -> Optional[_T]: ...
@overload
def third(coll: Tuple[Any, Any, _T, Any, Any]) -> Optional[_T]: ...
@overload
def third(coll: Tuple[Any, Any, _T, Any, Any, Any]) -> Optional[_T]: ...
@overload
def third(coll: Tuple[Any, Any, _T, Any, Any, Any, Any]) -> Optional[_T]: ...
@overload
def third(coll: Iterable[_T]|Any) -> Optional[_T]: ...

def third(coll: Iterable[_T]|Any) -> Optional[_T]:
    return _nth(coll, 2, 'third')


# --------------------------------
#       NTH

def nth(coll: Iterable[_T]|Any, n:int) -> Optional[_T]:
    return _nth(coll, n, 'nth')


# -------------------------------

@overload
def first_(coll: Tuple[_T]) -> _T: ...
@overload
def first_(coll: Tuple[_T, Any]) -> _T: ...
@overload
def first_(coll: Tuple[_T, Any, Any]) -> _T: ...
@overload
def first_(coll: Tuple[_T, Any, Any, Any]) -> _T: ...
@overload
def first_(coll: Tuple[_T, Any, Any, Any, Any]) -> _T: ...
@overload
def first_(coll: Tuple[_T, Any, Any, Any, Any, Any]) -> _T: ...
@overload
def first_(coll: Tuple[_T, Any, Any, Any, Any, Any, Any]) -> _T: ...
@overload
def first_(coll: Iterable[_T]|Any) -> _T: ...

def first_(coll: Iterable[_T]) -> _T:
    res = _nth(coll, 0, 'first_', __no_value())
    if isinstance(res, __no_value):
        raise MissingValueException(coll, 'first')
    return res


# -------------------------------

@overload
def second_(coll: Tuple[Any, _T]) -> _T: ...
@overload
def second_(coll: Tuple[Any, _T, Any]) -> _T: ...
@overload
def second_(coll: Tuple[Any, _T, Any, Any]) -> _T: ...
@overload
def second_(coll: Tuple[Any, _T, Any, Any, Any]) -> _T: ...
@overload
def second_(coll: Tuple[Any, _T, Any, Any, Any, Any]) -> _T: ...
@overload
def second_(coll: Tuple[Any, _T, Any, Any, Any, Any, Any]) -> _T: ...
@overload
def second_(coll: Iterable[_T]|Any) -> _T: ...

def second_(coll: Iterable):
    res = _nth(coll, 1, 'second_', __no_value())
    if isinstance(res, __no_value):
        raise MissingValueException(coll, 'second')
    return res


def nth_(coll: Iterable[_T], n:int) -> _T:
    res = _nth(coll, n, f'nth_{n}', __no_value())
    if isinstance(res, __no_value):
        raise MissingValueException(coll, f'nth_{n}')
    return res