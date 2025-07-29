"""
KotMap: A Python implementation of Kotlin's Map interface with snake_case naming convention.
"""

from __future__ import annotations

from typing import TypeVar, Generic, Callable, Optional, Dict, Iterator, Any, Tuple, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from kotcollections import KotMutableMap, KotList, KotSet

K = TypeVar('K')
V = TypeVar('V')
R = TypeVar('R')


class KotMap(Generic[K, V]):
    """A Python implementation of Kotlin's Map interface.
    
    This class provides all methods from Kotlin's Map interface with snake_case naming,
    maintaining type safety and immutability.
    """

    def __init__(self, elements: Optional[Dict[K, V] | List[Tuple[K, V]] | Iterator[Tuple[K, V]]] = None):
        """Initialize a KotMap with optional elements.
        
        Args:
            elements: Initial elements for the map (dict, list of tuples, or iterator of tuples)
        """
        self._elements: Dict[K, V] = {}
        self._key_type: Optional[type] = None
        self._value_type: Optional[type] = None

        if elements is not None:
            if isinstance(elements, dict):
                for key, value in elements.items():
                    self._put_with_type_check(key, value)
            elif isinstance(elements, list):
                for key, value in elements:
                    self._put_with_type_check(key, value)
            else:  # Iterator
                for key, value in elements:
                    self._put_with_type_check(key, value)

    def _put_with_type_check(self, key: K, value: V) -> None:
        """Add a key-value pair with type checking."""
        # Set key type
        if self._key_type is None and key is not None:
            self._key_type = type(key) if not isinstance(key, KotMap) else KotMap

        # Set value type
        if self._value_type is None and value is not None:
            self._value_type = type(value) if not isinstance(value, KotMap) else KotMap

        # Check key type
        if key is not None and self._key_type is not None:
            if isinstance(key, KotMap) and self._key_type == KotMap:
                pass  # KotMap keys are allowed
            elif not isinstance(key, KotMap) and not isinstance(key, self._key_type):
                raise TypeError(f"All keys must be of type {self._key_type.__name__}, got {type(key).__name__}")

        # Check value type
        if value is not None and self._value_type is not None:
            if isinstance(value, KotMap) and self._value_type == KotMap:
                pass  # KotMap values are allowed
            elif not isinstance(value, KotMap) and not isinstance(value, self._value_type):
                raise TypeError(f"All values must be of type {self._value_type.__name__}, got {type(value).__name__}")

        self._elements[key] = value

    # Basic Map operations

    def is_empty(self) -> bool:
        """Returns true if the map is empty."""
        return len(self._elements) == 0

    def is_not_empty(self) -> bool:
        """Returns true if the map is not empty."""
        return len(self._elements) > 0

    @property
    def size(self) -> int:
        """Returns the size of the map."""
        return len(self._elements)

    def contains_key(self, key: K) -> bool:
        """Returns true if the map contains the specified key."""
        return key in self._elements

    def contains_value(self, value: V) -> bool:
        """Returns true if the map maps one or more keys to the specified value."""
        return value in self._elements.values()

    # Access operations

    def get(self, key: K) -> Optional[V]:
        """Returns the value corresponding to the given key, or null if such a key is not present in the map."""
        return self._elements.get(key)

    def get_or_default(self, key: K, default_value: V) -> V:
        """Returns the value corresponding to the given key, or default_value if such a key is not present in the map."""
        return self._elements.get(key, default_value)

    def get_or_else(self, key: K, default_value: Callable[[], V]) -> V:
        """Returns the value for the given key. If the key is not found, calls the defaultValue function."""
        if key in self._elements:
            return self._elements[key]
        return default_value()

    def get_or_null(self, key: K) -> Optional[V]:
        """Returns the value corresponding to the given key, or null if such a key is not present in the map."""
        return self._elements.get(key)

    def get_or_none(self, key: K) -> Optional[V]:
        """Pythonic alias for get_or_null()."""
        return self.get_or_null(key)

    def get_value(self, key: K) -> V:
        """Returns the value for the given key or throws an exception if the key is missing in the map."""
        if key not in self._elements:
            raise KeyError(f"Key {key} is missing in the map.")
        return self._elements[key]

    # Collection views

    @property
    def keys(self) -> 'KotSet[K]':
        """Returns a read-only Set of all keys in this map."""
        from kotcollections import KotSet
        return KotSet(list(self._elements.keys()))

    @property
    def values(self) -> 'KotList[V]':
        """Returns a read-only Collection of all values in this map."""
        from kotcollections import KotList
        return KotList(self._elements.values())

    @property
    def entries(self) -> 'KotSet[Tuple[K, V]]':
        """Returns a read-only Set of all key/value pairs in this map."""
        from kotcollections import KotSet
        return KotSet(list(self._elements.items()))

    # Checking operations

    def all(self, predicate: Callable[[K, V], bool]) -> bool:
        """Returns true if all entries match the given predicate."""
        return all(predicate(k, v) for k, v in self._elements.items())

    def any(self, predicate: Callable[[K, V], bool]) -> bool:
        """Returns true if at least one entry matches the given predicate."""
        return any(predicate(k, v) for k, v in self._elements.items())

    def none(self, predicate: Callable[[K, V], bool]) -> bool:
        """Returns true if no entries match the given predicate."""
        return not any(predicate(k, v) for k, v in self._elements.items())

    def count(self, predicate: Optional[Callable[[K, V], bool]] = None) -> int:
        """Returns the number of entries matching the given predicate."""
        if predicate is None:
            return self.size
        return sum(1 for k, v in self._elements.items() if predicate(k, v))

    # Filtering operations

    def filter(self, predicate: Callable[[K, V], bool]) -> 'KotMap[K, V]':
        """Returns a map containing only entries matching the given predicate."""
        filtered_pairs = [(k, v) for k, v in self._elements.items() if predicate(k, v)]
        return KotMap(filtered_pairs)

    def filter_not(self, predicate: Callable[[K, V], bool]) -> 'KotMap[K, V]':
        """Returns a map containing only entries not matching the given predicate."""
        filtered_pairs = [(k, v) for k, v in self._elements.items() if not predicate(k, v)]
        return KotMap(filtered_pairs)

    def filter_keys(self, predicate: Callable[[K], bool]) -> 'KotMap[K, V]':
        """Returns a map containing all entries with keys matching the given predicate."""
        filtered_pairs = [(k, v) for k, v in self._elements.items() if predicate(k)]
        return KotMap(filtered_pairs)

    def filter_values(self, predicate: Callable[[V], bool]) -> 'KotMap[K, V]':
        """Returns a map containing all entries with values matching the given predicate."""
        filtered_pairs = [(k, v) for k, v in self._elements.items() if predicate(v)]
        return KotMap(filtered_pairs)

    def filter_not_null(self) -> 'KotMap[K, V]':
        """Returns a map containing only entries with non-null values."""
        filtered_pairs = [(k, v) for k, v in self._elements.items() if v is not None]
        return KotMap(filtered_pairs)

    def filter_not_none(self) -> 'KotMap[K, V]':
        """Pythonic alias for filter_not_null()."""
        return self.filter_not_null()

    # Transformation operations

    def map(self, transform: Callable[[K, V], R]) -> 'KotList[R]':
        """Returns a list containing the results of applying the given transform function to each entry."""
        from kotcollections import KotList
        return KotList([transform(k, v) for k, v in self._elements.items()])

    def map_keys(self, transform: Callable[[K, V], R]) -> 'KotMap[R, V]':
        """Returns a new map with entries having the keys obtained by applying the transform function to each entry."""
        transformed_pairs = [(transform(k, v), v) for k, v in self._elements.items()]
        return KotMap(transformed_pairs)

    def map_values(self, transform: Callable[[K, V], R]) -> 'KotMap[K, R]':
        """Returns a new map with entries having the values obtained by applying the transform function to each entry."""
        transformed_pairs = [(k, transform(k, v)) for k, v in self._elements.items()]
        return KotMap(transformed_pairs)

    def map_not_null(self, transform: Callable[[K, V], Optional[R]]) -> 'KotList[R]':
        """Returns a list containing only the non-null results of applying the given transform function."""
        from kotcollections import KotList
        results = []
        for k, v in self._elements.items():
            result = transform(k, v)
            if result is not None:
                results.append(result)
        return KotList(results)

    def map_not_none(self, transform: Callable[[K, V], Optional[R]]) -> 'KotList[R]':
        """Pythonic alias for map_not_null()."""
        return self.map_not_null(transform)

    def flat_map(self, transform: Callable[[K, V], Iterator[R]]) -> 'KotList[R]':
        """Returns a single list of all elements yielded from results of transform function."""
        from kotcollections import KotList
        results = []
        for k, v in self._elements.items():
            results.extend(transform(k, v))
        return KotList(results)

    # Conversion operations

    def to_list(self) -> List[Tuple[K, V]]:
        """Returns a List containing all key-value pairs."""
        return list(self._elements.copy().items())

    def to_dict(self) -> Dict[K, V]:
        """Returns a Python dict containing all key-value pairs."""
        return dict(self._elements.copy())

    def to_kot_map(self) -> 'KotMap[K, V]':
        """Returns a KotMap containing all key-value pairs."""
        return KotMap(self._elements.copy())

    def to_kot_mutable_map(self) -> 'KotMutableMap[K, V]':
        """Returns a KotMutableMap containing all key-value pairs."""
        from kotcollections.kot_mutable_map import KotMutableMap
        return KotMutableMap(self._elements.copy())

    # Action operations

    def for_each(self, action: Callable[[K, V], None]) -> None:
        """Performs the given action on each entry."""
        for k, v in self._elements.items():
            action(k, v)

    def on_each(self, action: Callable[[K, V], None]) -> 'KotMap[K, V]':
        """Performs the given action on each entry and returns the map itself."""
        for k, v in self._elements.items():
            action(k, v)
        return self

    # Finding operations

    def max_by(self, selector: Callable[[K, V], Any]) -> Optional[Tuple[K, V]]:
        """Returns the entry yielding the largest value of the given function."""
        if self.is_empty():
            return None
        return max(self._elements.items(), key=lambda item: selector(item[0], item[1]))

    def max_by_or_null(self, selector: Callable[[K, V], Any]) -> Optional[Tuple[K, V]]:
        """Returns the entry yielding the largest value of the given function or null if there are no entries."""
        return self.max_by(selector)

    def max_by_or_none(self, selector: Callable[[K, V], Any]) -> Optional[Tuple[K, V]]:
        """Pythonic alias for max_by_or_null()."""
        return self.max_by_or_null(selector)

    def min_by(self, selector: Callable[[K, V], Any]) -> Optional[Tuple[K, V]]:
        """Returns the entry yielding the smallest value of the given function."""
        if self.is_empty():
            return None
        return min(self._elements.items(), key=lambda item: selector(item[0], item[1]))

    def min_by_or_null(self, selector: Callable[[K, V], Any]) -> Optional[Tuple[K, V]]:
        """Returns the entry yielding the smallest value of the given function or null if there are no entries."""
        return self.min_by(selector)

    def min_by_or_none(self, selector: Callable[[K, V], Any]) -> Optional[Tuple[K, V]]:
        """Pythonic alias for min_by_or_null()."""
        return self.min_by_or_null(selector)

    # String representation

    def join_to_string(
        self, separator: str = ", ", prefix: str = "", postfix: str = "",
        limit: int = -1, truncated: str = "...",
        transform: Optional[Callable[[K, V], str]] = None
    ) -> str:
        """Creates a string from all the entries separated using separator."""
        if transform is None:
            transform = lambda k, v: f"{k}={v}"

        items = []
        for i, (k, v) in enumerate(self._elements.items()):
            if limit >= 0 and i >= limit:
                items.append(truncated)
                break
            items.append(transform(k, v))

        return prefix + separator.join(items) + postfix

    # Operator methods

    def plus(self, other: 'KotMap[K, V]' | Dict[K, V] | Tuple[K, V]) -> 'KotMap[K, V]':
        """Returns a map containing all entries from this map and the given map/pair.
        
        If a key is present in both maps, the value from the other map will be used.
        """
        from kotcollections import KotList
        
        new_elements = dict(self._elements)

        if isinstance(other, tuple):
            key, value = other
            new_elements[key] = value
        elif isinstance(other, KotMap):
            new_elements.update(other._elements)
        elif isinstance(other, KotList):
            # Support KotList of pairs
            for item in other:
                if isinstance(item, tuple) and len(item) == 2:
                    key, value = item
                    new_elements[key] = value
                else:
                    raise ValueError(f"Expected a tuple of (key, value), got {type(item)}")
        else:  # Dict
            new_elements.update(other)

        return KotMap(new_elements)

    def minus(self, key: K | List[K] | Set[K]) -> 'KotMap[K, V]':
        """Returns a map containing all entries from this map except those whose keys are in the given collection."""
        from kotcollections import KotSet
        
        if isinstance(key, (list, set)):
            new_elements = {k: v for k, v in self._elements.items() if k not in key}
        elif isinstance(key, KotSet):
            # Convert KotSet to set for efficient lookup
            key_set = set(key)
            new_elements = {k: v for k, v in self._elements.items() if k not in key_set}
        else:
            new_elements = {k: v for k, v in self._elements.items() if k != key}

        return KotMap(new_elements)

    def with_default(self, default_value: Callable[[K], V]) -> 'KotMapWithDefault[K, V]':
        """Returns a wrapper of this map having the implicit default value provided by the specified function."""
        return KotMapWithDefault(self, default_value)

    # Python special methods

    def __len__(self) -> int:
        """Return the number of entries in the map."""
        return self.size

    def __contains__(self, key: K) -> bool:
        """Check if a key is in the map."""
        return self.contains_key(key)

    def __getitem__(self, key: K) -> V:
        """Get value by key using [] operator."""
        if key not in self._elements:
            raise KeyError(f"Key {key} not found in map")
        return self._elements[key]

    def __iter__(self) -> Iterator[K]:
        """Iterate over keys."""
        return iter(self._elements)

    def __repr__(self) -> str:
        """Return string representation of the map."""
        return f"KotMap({dict(self._elements)})"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another KotMap."""
        if not isinstance(other, KotMap):
            return False
        return self._elements == other._elements

    def __add__(self, other: 'KotMap[K, V]' | Dict[K, V] | Tuple[K, V]) -> 'KotMap[K, V]':
        """Implement + operator for maps."""
        return self.plus(other)

    def __sub__(self, key: K | List[K] | Set[K]) -> 'KotMap[K, V]':
        """Implement - operator for maps."""
        return self.minus(key)

    def __hash__(self) -> int:
        """Return hash of the map."""
        # Since KotMap is immutable, we can cache the hash
        if not hasattr(self, '_cached_hash'):
            items = tuple(sorted(self._elements.items()))
            self._cached_hash = hash(items)
        return self._cached_hash


class KotMapWithDefault(KotMap[K, V]):
    """A wrapper class that provides a default value for missing keys.
    
    This class wraps a KotMap and provides a default value function that
    is called when a key is not found in the map.
    """

    def __init__(self, map: KotMap[K, V], default_value: Callable[[K], V]):
        """Initialize with a map and a default value function.
        
        Args:
            map: The underlying KotMap
            default_value: Function that provides default values for missing keys
        """
        # Copy the elements from the original map
        super().__init__(map._elements)
        self._default_value_function = default_value

    def get(self, key: K) -> V:
        """Returns the value corresponding to the given key, or the default value if the key is not present."""
        if key in self._elements:
            return self._elements[key]
        return self._default_value_function(key)

    def get_or_default(self, key: K, default_value: V) -> V:
        """Returns the value corresponding to the given key, or default_value if such a key is not present."""
        # This overrides the parent method to use the map's default if no explicit default is needed
        return self.get(key)

    def get_or_else(self, key: K, default_value: Callable[[], V]) -> V:
        """Returns the value for the given key. If the key is not found, calls the defaultValue function."""
        if key in self._elements:
            return self._elements[key]
        # Use the map's default value function, not the provided one
        return self._default_value_function(key)

    def get_value(self, key: K) -> V:
        """Returns the value for the given key, using the default if the key is missing."""
        return self.get(key)

    def __getitem__(self, key: K) -> V:
        """Get value by key using [] operator, with default value support."""
        return self.get(key)

    def __repr__(self) -> str:
        """Return string representation of the map with default."""
        return f"KotMapWithDefault({dict(self._elements)}, default_function)"
