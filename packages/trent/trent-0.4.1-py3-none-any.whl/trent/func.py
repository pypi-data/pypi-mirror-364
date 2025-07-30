from typing import Any, Callable, Dict, Hashable, Iterable, Optional, Sequence, TypeVar

from trent.nth import __no_value, nth




# ======================================================

_T = TypeVar('_T')
_T2 = TypeVar('_T2')

NV = __no_value()

def identity(val: _T) -> _T:
    return val


# ============================================================================
#               UTIL

def __get(m: Dict[Any, _T], key, default: _T2 = None) -> _T|_T2:
    return m.get(key, default)
    

def getter(key, default: _T2 = None) -> Callable[[Dict[Any, _T]], _T|_T2]:
    def __f(__m: Dict[Any, _T]) -> _T | _T2:
        return __get(__m, key, default)
    return __f


def gtr(key, default: _T2 = None, /) -> Callable[[Dict[Any, _T]], _T|_T2]:
    return getter(key, default)

def gtr_(key:Hashable, _type: type[_T], /) -> Callable[[Dict[Any, Any]], _T]:
    def __f(__m: Dict[Any, _T]):
        _res = __get(__m, key, NV)
        if isinstance(_res, __no_value):
            raise Exception(f'Missing value by key: {key}, from map: {__m}')
        return _res
    return __f


def isnone(val: Any) -> bool:
    return val is None


if __name__ == '__main__':
    d = {'foo': 1}
    
    f = gtr_('foo', int)
    
    res = f(d)