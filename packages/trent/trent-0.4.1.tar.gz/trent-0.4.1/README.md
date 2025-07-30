# trent
Convenient Collection/Sequence/Iterable processing for python.

Inspired by Clojure mapping and threading macros.

Supprot full python12 (and later vesrsion) typing, unlike default `map` and `filter` functions.
Which allows for production-grade development. 
Provides some work-around for python typing issues (like inability to filter out types from aggregate type).
Provides some auxiliary side funtions, like `first`, `second`, `nth`, `getter` etc.
Also, provide some additional usefull functionality, like `group_by` and `partition_by` (see more examples below)


#### What is it for
Writing **functional**, fully **typehinted** code in a style of Common Lisp / Clojure **mappings**, with convenience of Clojure funcall **threading** (->, ->>, as-> macroses), but with python native syntax (without trying to force-fit any other syntax in)

And more:
- Processing *Iterables* in a **functional** manner, with **lazy** evaluation (in most cases)
- Iterating, concating, grouping and collecting elements of given sequences quickly.
- **Prototyping** code in quick, readable and maintanable manner.
- Writing **fully typehinted** code (unlike default map/filter)
- Built-in **assyncronous** calls (mapping, filtering etc.)
- **Reducing** resulting iterables.


#### What is it NOT for
**trent** - is keps simple for a reason. Don't try to use it for more than it designed for.
- Not for high load / high performance Sequences processing (although - it supports parallel-map)
- Not for processing table-like data. Just use pandas/polars/pyspark for that. `trent` is more suitable for processing each element individually