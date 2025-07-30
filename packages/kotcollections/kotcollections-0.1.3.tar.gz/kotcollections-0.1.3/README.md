# KotCollections - Kotlin Collections API for Python

[![image](https://img.shields.io/pypi/v/kotcollections.svg)](https://pypi.org/project/kotcollections/)
[![image](https://img.shields.io/pypi/l/kotcollections.svg)](https://pypi.org/project/kotcollections/)
[![image](https://img.shields.io/pypi/pyversions/kotcollections.svg)](https://pypi.org/project/kotcollections/)
[![image](https://img.shields.io/github/contributors/lalcs/kotcollections.svg)](https://github.com/lalcs/kotcollections/graphs/contributors)
[![image](https://img.shields.io/pypi/dm/kotcollections)](https://pypistats.org/packages/kotcollections)
[![Unit Tests](https://github.com/Lalcs/kotcollections/actions/workflows/unittest.yml/badge.svg)](https://github.com/Lalcs/kotcollections/actions/workflows/unittest.yml)

kotcollections is a Python library that fully reproduces Kotlin's Collections interfaces. It brings Kotlin's rich
collection operations to Python developers with List, Set, and Map implementations.

## Installation

```bash
pip install kotcollections
```

## Features

- Complete implementation of Kotlin's List, Set, and Map interfaces using Python's snake_case naming convention
- Pythonic `_none` aliases for all `_null` methods (e.g., both `first_or_null()` and `first_or_none()` are available)
- Provides read-only and mutable variants:
    - `KotList` and `KotMutableList` for list operations
    - `KotSet` and `KotMutableSet` for set operations
    - `KotMap` and `KotMutableMap` for map operations
- Full type safety with type hints
- Runtime type checking to ensure single element type (similar to Kotlin's generic type system)
- 100% test coverage

## Type Safety

KotList and KotSet implement runtime type checking similar to Kotlin's type system. Once a collection is created with
elements of a specific type, it can only contain elements of that same type.

### How It Works

- The first element added to a collection determines its element type
- All subsequent elements must be of the same type
- Collections can be nested (similar to `List<List<T>>` or `Set<Set<T>>` in Kotlin)
- Type checking occurs on initialization and all modification operations

### Examples

```python
# Valid: All elements are the same type
lst = KotList([1, 2, 3])  # KotList[int]
s = KotSet(['a', 'b', 'c'])  # KotSet[str]

# Invalid: Mixed types will raise TypeError
try:
    lst = KotList([1, 'a', 2])  # TypeError!
except TypeError as e:
    print(e)  # Cannot add element of type 'str' to KotList[int]

# Valid: Nested collections
nested_lists = KotList(
    [
        KotList([1, 2]),
        KotList([3, 4])
    ]
)  # KotList[KotList]

nested_sets = KotSet(
    [
        KotSet([1, 2]),
        KotSet([3, 4])
    ]
)  # KotSet[KotSet]

# Mutable collections also enforce type safety
mutable_list = KotMutableList([1, 2, 3])
mutable_list.add(4)  # OK: same type

mutable_set = KotMutableSet(['a', 'b', 'c'])
mutable_set.add('d')  # OK: same type

try:
    mutable_list.add('string')  # TypeError!
except TypeError as e:
    print(e)  # Cannot add element of type 'str' to KotList[int]

# Empty collections determine type on first element
empty_list = KotMutableList()
empty_list.add('first')  # Now it's KotList[str]

empty_set = KotMutableSet()
empty_set.add(42)  # Now it's KotSet[int]
```

### Comparison with Kotlin

This type safety implementation provides similar guarantees to Kotlin's generic type system:

| Kotlin                   | kotcollections (Python)                               |
|--------------------------|-------------------------------------------------------|
| `List<Int>`              | `KotList([1, 2, 3])`                                  |
| `List<String>`           | `KotList(['a', 'b', 'c'])`                            |
| `List<List<Int>>`        | `KotList([KotList([1, 2]), KotList([3, 4])])`         |
| `Set<Double>`            | `KotSet([1.0, 2.0, 3.0])`                             |
| `Map<String, Int>`       | `KotMap({"one": 1, "two": 2})`                        |
| `Map<Int, List<String>>` | `KotMap({1: KotList(["a", "b"]), 2: KotList(["c"])})` |

The main difference is that Kotlin performs compile-time type checking, while kotcollections performs runtime type
checking.

## Pythonic Aliases

To provide a more Pythonic API, all methods ending with `_null` have corresponding `_none` aliases:

```python
# All these _null methods have _none aliases
lst = KotList([1, 2, None, 3, None])

# Access methods
print(lst.get_or_null(10))  # None
print(lst.get_or_none(10))  # None (same result)
print(lst.first_or_none())  # 1
print(lst.last_or_none())  # None

# Transformation methods  
result = lst.map_not_none(lambda x: x * 2 if x else None)  # [2, 4, 6]

# Filtering
non_empty = lst.filter_not_none()  # KotList([1, 2, 3])

# Aggregation
print(lst.max_or_none())  # 3
print(lst.min_or_none())  # 1
```

Both naming conventions are fully supported and can be used interchangeably based on your preference.

## Quick Start

```python
from kotcollections import KotList, KotMutableList, KotSet, KotMutableSet, KotMap, KotMutableMap

# Lists - ordered, allows duplicates
numbers = KotList([1, 2, 3, 2, 1])
print(numbers.distinct().to_list())  # [1, 2, 3]

# Sets - unordered, no duplicates
unique_numbers = KotSet([1, 2, 3, 2, 1])
print(unique_numbers.to_list())  # [1, 2, 3] (order not guaranteed)

# Maps - key-value pairs
scores = KotMap({"Alice": 90, "Bob": 85, "Charlie": 95})
print(scores.get("Alice"))  # 90

# Functional operations work on all
doubled_list = numbers.map(lambda x: x * 2)
doubled_set = unique_numbers.map(lambda x: x * 2)
high_scores = scores.filter(lambda k, v: v >= 90)

# Mutable variants allow modifications
mutable_list = KotMutableList([1, 2, 3])
mutable_list.add(4)

mutable_set = KotMutableSet([1, 2, 3])
mutable_set.add(4)

mutable_map = KotMutableMap({"a": 1})
mutable_map.put("b", 2)
```

## Basic Usage

```python
from kotcollections import KotList, KotMutableList, KotMap, KotMutableMap

# Create a read-only list
lst = KotList([1, 2, 3, 4, 5])

# Create a mutable list
mutable_lst = KotMutableList([1, 2, 3, 4, 5])

# Create a read-only map
m = KotMap({"a": 1, "b": 2, "c": 3})

# Create a mutable map
mutable_m = KotMutableMap({"x": 10, "y": 20})
```

## Kotlin to Python Naming Convention

All Kotlin methods are available with Python's snake_case naming convention. Additionally, all methods ending with
`_null` have Pythonic `_none` aliases:

| Kotlin            | Python (Primary)    | Python (Alias)      |
|-------------------|---------------------|---------------------|
| `getOrNull()`     | `get_or_null()`     | `get_or_none()`     |
| `firstOrNull()`   | `first_or_null()`   | `first_or_none()`   |
| `mapIndexed()`    | `map_indexed()`     | -                   |
| `filterNotNull()` | `filter_not_null()` | `filter_not_none()` |
| `associateBy()`   | `associate_by()`    | -                   |
| `joinToString()`  | `join_to_string()`  | -                   |

Note: Both naming styles (`_null` and `_none`) can be used interchangeably based on your preference.

## API Reference

For detailed documentation of all available methods, please refer to the [API Reference](docs/API_REFERENCE.md).

## Performance Considerations

- `KotList` internally uses Python's standard list, so basic operation performance is equivalent to standard lists
- `KotSet` internally uses Python's standard set, providing O(1) average case for add, remove, and contains operations
- `KotMap` internally uses Python's standard dict, providing O(1) average case for get, put, and contains operations
- When using method chaining extensively, be aware that each method creates a new collection, which may impact memory
  usage
- For large datasets, consider generator-based implementations

## License

MIT License