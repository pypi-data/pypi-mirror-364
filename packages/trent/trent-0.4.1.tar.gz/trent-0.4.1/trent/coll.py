from __future__ import annotations

import concurrent.futures as conc
from functools import cache, reduce
from itertools import chain, groupby, takewhile
from pprint import pprint
from time import sleep
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    overload,
)

from funcy import complement, filter, take

from trent.coll_aux import DistinctFilter, PartByCounter, PartCounter, Rangifier
from trent.concur import CPU_COUNT, TRENT_THREADPOOL
from trent.func import identity, isnone
from trent.nth import MissingValueException, first, first_, second, second_

T = TypeVar('T')
T1 = TypeVar('T1')
T2 = TypeVar('T2')
S = TypeVar('S')


class __no_value():
    def __init__(self) -> None:
        pass


class NestedIterationExceprion(Exception):
    def __str__(self) -> str:
        return 'Nested iteration over `coll` class is invalid !!!'


class EmptyCollectionException(Exception):
    def __init__(self, msg: str) -> None:
        self.__msg = msg
    
    def __str__(self) -> str:
        return f'Collection is empty! {self.__msg}'


class icoll(Iterable[T]):
    """Represents a lazy sequence of type `T`"""    
    def __init__(self, collection: Optional[Iterable[T]] = None) -> None:
        """Create a lazy sequence `icoll`, with given Iterables collection. Or empty - if None.

        Args:
            collection (Optional[Iterable[T]], optional): Initial sequence to be iterated over. Defaults to None.
        """        
        self._coll: Iterable[T]
        self._iterator: Iterator[T]
        self._is_iterated: bool = False
        if collection is not None:
            self._coll = collection
        else:
            self._coll = []
    
    @property
    def collection(self) -> Iterable[T]:
        """Iternal Iterable collection. WARNING: iterating over it outside of class methods may break youre code.

        Returns:
            Iterable[T]: Internal Iterable sequnce
        """        
        return self._coll
    
    # =================================================================
    #           TODO
    
    def _init_collection(self, collection:Optional[Iterable[T]]=None) -> Iterable[T]:
        if collection is None:
            return []
        elif isinstance(collection, icoll):
            return collection.collection
        elif isinstance(collection, Iterable):
            return collection
        else:
            raise Exception(f'Invalid collection type: {type(collection)}. Expected Iterable!')
    
    
    def _step(self, __coll: Iterable[S]) -> icoll[S]:
        return icoll(__coll)

    # ==================================================================
    #           MAPS
    
    def map(self, f: Callable[[T], S]) -> icoll[S]:
        """Maps over the elements of collection with function `f(el: T) -> S`, and retrun a new collection icoll[S].

        Args:
            f (Callable[[T], S]): Callable to process sequence elements.

        Returns:
            icoll[S]: New collection.
        """        
        return self._step(map(f, self._coll))
    
    
    def pmap(self, f: Callable[[T], S]) -> icoll[S]:
        """Performes `map` in parallel.

        Args:
            f (Callable[[T], S]): Fuction to map elements with

        Returns:
            icoll[S]: New collection.
        """        
        __map = TRENT_THREADPOOL.map(f, self._coll)
        return self._step(__map)
    
    
    def pmap_(self, f: Callable[[T], S], threads: int = CPU_COUNT) -> icoll[S]:
        """Performed `map` in parallel. And a number of threads to use can be defined.

        Args:
            f (Callable[[T], S]): Function to map elements with
            threads (int, optional): A number of async threads to use for maing. Defaults to CPU_COUNT.

        Returns:
            icoll[S]: New collection
        """        
        assert threads >= 1, 'Async Thread count CAN NOT be < 1'
        if threads == 1:
            return self.map(f)
        with conc.ThreadPoolExecutor(threads) as p:
            __map = p.map(f, self._coll)
        return self._step(__map)
    
    
    def mapcat(self, f: Callable[[T], Iterable[T1]]) -> icoll[T1]:
        """Maps elements with function `f(el) -> Iterable`, and concatenates resulting collectinns of iterables.

        Args:
            f (Callable[[T], Iterable[T1]]): Function to map elements with. MUST return an Iterable.

        Returns:
            icoll[T1]: New collection.
        """        
        m = map(f, self._coll)
        m = chain(* m)
        return self._step(m)
    
    
    def cat(self) -> icoll[Any]:
        """Concatenates sequence of Iterables into one sequence.
        ```
        c = seq([[1, 2], [3, 4]]).cat()
        assert c.to_list() == [1, 2, 3, 4]
        ```

        Returns:
            icoll[Any]: New collection
        """
        return self.mapcat(identity) # type: ignore
    
    
    def catmap(self, f: Callable[[Any], T1]) -> icoll[T1]:
        """Concatenate sequence (as in cat()), and than - performe a `map` over elements with funcion `f`

        Args:
            f (Callable[[Any], T1]): Function to map elements with

        Returns:
            icoll[T1]: New collection
        """        
        return self.cat().map(f)
    
    
    def apply(self, f:Callable[[T], Optional[Any]]) -> icoll[T]:
        """Applyes function  `f` to all elements, but not maps elements to new values. Resulting coll witll have the same elements.
        Usefull for:
            - Updating dict elements in icoll[dict]
            - calling methods on class-objects:
             
            ```
            lst: icoll[God] = lst.apply(Dog.bark)
            ```
            - calling functions in icoll[Callable]

        Args:
            f (Callable[[T], Optional[Any]]): Function to apply to elements

        Returns:
            icoll[T]: Collection of the same elements
        """        
        def __apply(el: T) -> T:
            f(el)
            return el
        return self.map(__apply)
    
    
    def filter(self, f: Callable[[T], Any]) -> icoll[T]:
        """Filter elements in sequence by predicate `f`. (remove `el` if `not f(el)y)

        Args:
            f (Callable[[T], Any]): Predicate function

        Returns:
            icoll[T]: New collection
        """        
        return self._step(filter(f, self._coll))
    
    
    def remove(self, f: Callable[[T], Any]) -> icoll[T]:
        """Removed elements from sequence by predicate `f`. (remove `el` if `f(el)`)

        Args:
            f (Callable[[T], Any]): Predicate function

        Returns:
            icoll[T]: New collection
        """        
        _f = complement(f)
        return self.filter(_f)
    
    
    @overload
    def remove_none(self) -> icoll[Any]: ...
    @overload
    def remove_none(self, * _types: type[S]) -> icoll[S]: ...
    
    def remove_none(self, * _types): # type: ignore
        """WARNING: removes typehinting for given `coll`. Returns icoll[Any].
        Use only for avoiding typehint warnings about None type!

        Returns:
            icoll[Any]: icoll[T] with all None removed
        """        
        return self.remove(isnone)
    
    
    def unique(self) -> icoll[T]:
        """Remove all duplicate elements in sequence.
        WARN: demands extra RAM.

        Returns:
            icoll[T]: New collection of unique elements.
        """        
        return self.distinct_by(identity)
    
    
    def distinct_by(self, f:Callable[[Any], Hashable]=identity) -> icoll[T]:
        """Remove duplicate elements by predicate `f`.
        (Remove `el` of `f(el)` is already present)

        Args:
            f (Callable[[Any], Hashable], optional): Predicate function. Defaults to identity.

        Returns:
            icoll[T]: New collection.
        """        
        __pred = DistinctFilter(f)
        return self.filter(__pred)
    
    # =================================================================
    #           TAKE
    
    def take(self, n: int)-> icoll[T]:
        """Take `n` elements from sequence."""        
        assert n >= 0, 'You can only `take` >= 0 elements!'
        return self._step(take(n, self._coll))
    
    def takewhile(self, predicate:Callable[[T], bool]) -> icoll[T]:
        """Take elements while `predicate(el)`.

        Args:
            predicate (Callable[[T], bool]): Predicate function

        Returns:
            icoll[T]: New collection
        """        
        return self._step(takewhile(predicate, self._coll))
    
    
    def partition(self, partition_size: int, /) -> icoll[list[T]]:
        """Partition sequence into chunks of size `partition_size`.

        Args:
            partition_size (int): Size of partitions

        Returns:
            icoll[list[T]]: New collection.
        """        
        groups = groupby(self._coll, PartCounter(partition_size))
        c = map(second_, groups)
        c = map(list, c)
        return self._step(c)
    
    
    def partition_by(self, pred: Callable[[T], Any]) -> icoll[list[T]]:
        """Partition sequence int ochunks devided by predicate `pred`.
        Where every time `pred(value)` return True - a new partition will be created.
        ```
        c = icoll(range(6))
        c.partition_by(lambda n: n % 2 == 0).to_list() == [[0, 1], [2, 3], [4, 5]]
        ```

        Args:
            pred (Callable[[T], Any]): Predicate to devide sequence into chunks by.

        Returns:
            icoll[list[T]]: New collection.
        """        
        groups = groupby(self._coll, PartByCounter(pred))
        c = map(second_, groups)
        c = map(list, c)
        return self._step(c)
        
    
    # ==================================================================
    #           PAIRED
    
    def pairmap(self, f:Callable[[Any, Any], T1]) -> icoll[T1]:
        """Map over paired elements (tuple, list, Iterable, etc.) with `f(arg1, arg2)` function.
        WARNING: sequence elements MUST be iterables.
        NOTE: Iterable elements can contain more than 2 elements, but extra values will be lost.
        NOTE: If elements contain less than 2 values - `None` will be passed to `f` instead.

        Args:
            f (Callable[[Any, Any], T1]): _description_

        Returns:
            icoll[T1]: _description_
        """        
        return self.map(lambda p: f(first(p), second(p)))
    
    
    def map_to_pair(self, f_key: Callable[[T], T1], f_val: Callable[[T], T2] = identity) -> icoll[Tuple[T1, T2]]:
        def __pair(val: T) -> Tuple[T1, T2]:
            return (f_key(val), f_val(val))
        return self.map(__pair)
    
    
    def group_by_to_dict(self, f:Callable[[T], T1], val_fn: Callable[[T], T2] = identity) -> Dict[T1, list[T2]]:
        def __group(val: T) -> Tuple[T1, T2]:
            return (f(val), val_fn(val))
        pairs = self.map(__group).to_list()
        res: dict[T1, list[T2]] = {}
        for p in pairs:
            k,v = p
            if k in res:
                res[k].append(v)
            else:
                res[k] = [v]
        return res
    
    
    def group_by(self, f:Callable[[T], T1], val_fn: Callable[[T], T2] = identity) -> icoll[tuple[T1, list[T2]]]:
        d = self.group_by_to_dict(f, val_fn)
        return self._step(d.items())
    
    
    @overload
    def groupmap(self) -> icoll[tuple[Any, Any]]: ...
    @overload
    def groupmap(self, f:Callable[[Any, Any], S]) -> icoll[S]: ...
    
    def groupmap(self, f:Optional[Callable[[Any, Any], S]]=None):
        def __unpack_group(group):
            key, vals = group
            return [(key, v) for v in vals]
        pairs = self.mapcat(__unpack_group)
        if f:
            return pairs.pairmap(f)
        return pairs
    
    
    def rangify(self) -> icoll[Tuple[T, T]]:
        __it = iter(self._coll)
        try:
            __init_val = first_(__it)
        except MissingValueException:
            raise EmptyCollectionException("Can't `rangify` an empty collection!")
        __f = Rangifier(__init_val)
        return self._step(map(__f, __it))
    
    
    # ==================================================================
    #           TRANSFORMATIONS
    
    def concat(self, *__iterables: Iterable[T]) -> icoll[T]:
        res = self._step(self._coll)
        for __it in __iterables:
            res.extend_(__it)
        return res
    
    def extend(self, __iterable: Iterable[T]) -> icoll[T]:
        return self.concat(__iterable)
    
    
    def conj(self, *vals: T):
        return self.concat(vals)
    
    
    def append(self, __val: T) -> icoll[T]:
        return self._step(self._coll).append_(__val)
    
    
    def cons(self, __val: T):
        return self._step(chain([__val], self._coll))

    
    def __add__(self, __iter: Iterable[T]) -> icoll[T]:
        return self.concat(__iter)
    
    # ===============================================================
    #   IN_PLACE TRANSFORMATIONS
    
    def extend_(self, __iterable: Iterable[T]) -> icoll[T]:
        """In-place extend. Addes `__iterable` to the end of `coll`.

        Args:
            __iterable (Iterable[T]): Iterable to be concatenated to the end

        Returns:
            coll[T]: Self
        """        
        if isinstance(__iterable, icoll):
            self._coll = chain(self._coll, __iterable.collection)
            return self
        self._coll = chain(self._coll, __iterable)
        return self
    
    def append_(self, __val: T) -> icoll[T]:
        self.extend_([__val])
        return self
    
    
    def cons_(self, __val: T):
        self._coll = chain([__val], self._coll)
    
    
    # =================================================================
    #           COLLECTING
    
    def to_list(self) -> list[T]:
        return list(self._coll)
    
    def to_set(self) -> set[T]:
        return set(self._coll)
    
    
    def collect(self, f: Callable[[list[T]], S] = identity) -> S:
        return f(self.to_list())
    
    
    
    @overload
    def reduce(self, f: Callable[[T, T], T]) -> T: ...
    @overload
    def reduce(self, f: Callable[[S, T], S], initial: S) -> S: ...
    
    def reduce(self, f: Callable, initial: Optional[S] = None) -> S | T:
        if initial is None:
            return reduce(f, self)
        return reduce(f, self, initial)
    
    
    
    # ================================================================
    #           ITERATION
    
    def _iter(self):
        if self._is_iterated:
            raise NestedIterationExceprion
        self._iterator = iter(self._coll)
        self._is_iterated = True
        return self
    
    def __iter__(self):
        return self._iter()
    
    
    def _next(self):
        try:
            return next(self._iterator)
        except StopIteration:
            self._is_iterated = False
            raise StopIteration
    
    def __next__(self) -> T:
        return self._next()
    
    def __repr__(self) -> str:
        # Persisting collection values. For easier debugging.
        # self._coll = list(self._coll)
        return f'coll({self._coll})'
    
    
    # ===============================================================
    #               UTIL
    
    def __group_pair_fn(self, f: Callable[[T], T1], val_fn: Callable[[T], T2] = identity) -> Callable[[T], Tuple[T1, T2]]:
        return lambda val: (f(val), val_fn(val))


class persistent_coll(icoll, Iterable[T]):
    def __init__(self, collection: Iterable | None = None) -> None:
        self.__buffer: list[T] = []
        self.__is_iterated: bool = False
        super().__init__(collection)
    
    
    def _step(self, __coll: Iterable[S]) -> icoll[S]:
        return persistent_coll(__coll)
    
    
    def _iter(self):
        if self.__is_iterated:
            raise NestedIterationExceprion
        self._iterator = iter(self._coll)
        self.__buffer = []
        self.__is_iterated = True
        return self
    
    def _next(self):
        try:
            res = next(self._iterator)
        except StopIteration:
            self._coll = self.__buffer
            self.__is_iterated = False
            raise StopIteration
        self.__buffer.append(res)
        return res
        
        


class paired_coll(icoll, Iterable[Tuple[T1, T2]]):
    def __init__(self, collection: Iterable[Tuple[T1, T2]] | Dict[T1, T2] | None = None) -> None:
        super().__init__(collection)
        
        
    
    
    
    def _init_collection(self, collection:Iterable[Tuple[T1, T2]]|Dict[T1, T2]|None = None) -> Iterable[Tuple[T1, T2]]:
        if collection is None:
            return []
        elif isinstance(collection, paired_coll):
            return collection._coll
        elif isinstance(collection, Dict):
            return collection.items() # type: ignore
        elif isinstance(collection, Iterable):
            return collection
        else:
            raise Exception(f'Invalid collection type: {type(collection)}. Expected Iterable!')
    
    
    # def __step(self, __coll: Iterable[Tuple[T1, T2]]) -> paired_coll[T1, T2]:
    #     return paired_coll(__coll)

    
    def pairmap(self, f:Callable[[T1, T2], S]) -> icoll[S]:
        return self.map(lambda p: f(first_(p), second_(p)))






if __name__ == '__main__':
    # c = paired_coll({1: 10}.items())
    # print(c)
    print(dict([(1,10), (2, 20)]))
    pass