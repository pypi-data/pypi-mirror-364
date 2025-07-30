from typing import Any, Callable, Generic, Hashable, Tuple, TypeVar


T = TypeVar('T')


class DistinctFilter(Generic[T]):
    def __init__(self, f:Callable[[T], Hashable]) -> None:
        self.__encounters = set()
        self.__f = f


    def __call__(self, val: T) -> bool:
        __val = self.__f(val)
        if __val in self.__encounters:
            return False
        self.__encounters.add(__val)
        return True


class Rangifier(Generic[T]):
    def __init__(self, init_val: T) -> None:
        self.__prev: T = init_val

    def __call__(self, val: T) -> Tuple[T, T]:
        res = (self.__prev, val)
        self.__prev = val
        return res


class PartCounter:
    def __init__(self, count: int) -> None:
        self.__count = count
        self.__i = 0
        self.__part_number = 0
        
    def __call__(self, *_) -> int:
        if self.__i >= self.__count:
            self.__i = 0
            self.__part_number += 1
        self.__i += 1
        return self.__part_number
    


class PartByCounter:
    def __init__(self, pred: Callable[[Any], bool]) -> None:
        self._pred = pred
        self.__part_number = 0
        
    def __call__(self, value) -> int:
        if self._pred(value):
            self.__part_number += 1
        return self.__part_number