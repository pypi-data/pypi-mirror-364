from typing import Iterable, Optional, TypeVar
from trent.coll import NestedIterationExceprion, icoll

T = TypeVar('T')

class pcoll(icoll, Iterable[T]):
    def __init__(self, collection: Optional[Iterable[T]] = None) -> None:
        self.__buffer: list[T]
        super().__init__(collection)
    
    
    def __iter__(self):
        if self._is_iterated:
            raise NestedIterationExceprion
        self.__buffer = []
        self._iterator = iter(self._coll)
        self._is_iterated = True
        return self
    
    
    def __next__(self) -> T:
        try:
            val = next(self._iterator)
        except StopIteration:
            self._coll = self.__buffer
            self._is_iterated = False
            raise StopIteration
        self.__buffer.append(val)
        return val