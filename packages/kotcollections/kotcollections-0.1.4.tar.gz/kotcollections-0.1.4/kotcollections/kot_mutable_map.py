"""
KotMutableMap: A Python implementation of Kotlin's MutableMap interface with snake_case naming convention.
"""

from __future__ import annotations

from typing import TypeVar, Dict, List, Iterator, Optional, Callable, Tuple, Type

from kotcollections.kot_map import KotMap

K = TypeVar('K')
V = TypeVar('V')



class KotMutableMap(KotMap[K, V]):
    """A Python implementation of Kotlin's MutableMap interface.
    
    This class extends KotMap with mutation methods, providing full
    Kotlin MutableMap functionality with snake_case naming.
    """

    def __init__(self, elements: Optional[Dict[K, V] | List[Tuple[K, V]] | Iterator[Tuple[K, V]]] = None):
        """Initialize a KotMutableMap with optional elements.
        
        Args:
            elements: Initial elements for the map (dict, list of tuples, or iterator of tuples)
        """
        super().__init__(elements)

    @classmethod
    def __class_getitem__(cls, types: Tuple[Type[K], Type[V]]) -> Type['KotMutableMap[K, V]']:
        """Enable KotMutableMap[KeyType, ValueType]() syntax for type specification.
        
        Example:
            animals_by_name = KotMutableMap[str, Animal]()
            animals_by_name.put("Buddy", Dog("Buddy"))
            animals_by_name.put("Whiskers", Cat("Whiskers"))
        """
        key_type, value_type = types
        
        class TypedKotMutableMap(cls):
            def __init__(self, elements=None):
                # Only set types if they are actual types, not type variables
                self._elements = {}
                self._key_type = key_type if isinstance(key_type, type) else None
                self._value_type = value_type if isinstance(value_type, type) else None
                # Now process elements with the correct types set
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
        
        # Set a meaningful name for debugging
        TypedKotMutableMap.__name__ = f"{cls.__name__}[{key_type.__name__}, {value_type.__name__}]"
        TypedKotMutableMap.__qualname__ = f"{cls.__qualname__}[{key_type.__name__}, {value_type.__name__}]"
        
        return TypedKotMutableMap

    @classmethod
    def of_type(cls, key_type: Type[K], value_type: Type[V], elements: Optional[Dict[K, V] | List[Tuple[K, V]] | Iterator[Tuple[K, V]]] = None) -> 'KotMutableMap[K, V]':
        """Create a KotMutableMap with specific key and value types.
        
        This is useful when you want to create a mutable map with parent types
        but only have instances of child types.
        
        Args:
            key_type: The type of keys this map will contain
            value_type: The type of values this map will contain
            elements: Optional initial elements
            
        Returns:
            A new KotMutableMap instance with the specified types
            
        Example:
            animals_by_name = KotMutableMap.of_type(str, Animal, [("Buddy", Dog("Buddy")), ("Whiskers", Cat("Whiskers"))])
            # or empty map
            animals_by_name = KotMutableMap.of_type(str, Animal)
            animals_by_name.put("Max", Dog("Max"))
        """
        # Use __class_getitem__ to create the same dynamic subclass
        typed_class = cls[key_type, value_type]
        return typed_class(elements)

    # Mutation operations

    def put(self, key: K, value: V) -> Optional[V]:
        """Associates the specified value with the specified key in the map.
        
        Returns:
            The previous value associated with the key, or null if the key was not present.
        """
        old_value = self._elements.get(key)
        self._put_with_type_check(key, value)
        return old_value

    def put_all(self, from_map: Dict[K, V] | 'KotMap[K, V]' | List[Tuple[K, V]]) -> None:
        """Updates this map with key/value pairs from the specified map."""
        if isinstance(from_map, KotMap):
            from_map = from_map._elements
        elif isinstance(from_map, list):
            from_map = dict(from_map)
        
        for key, value in from_map.items():
            self._put_with_type_check(key, value)

    def put_if_absent(self, key: K, value: V) -> Optional[V]:
        """Associates the specified value with the specified key only if it is not already associated.
        
        Returns:
            The current value associated with the key, or null if none and the new value was added.
        """
        if key in self._elements:
            return self._elements[key]
        self._put_with_type_check(key, value)
        return None

    def remove(self, key: K) -> Optional[V]:
        """Removes the specified key and its corresponding value from this map.
        
        Returns:
            The value associated with the key, or null if the key was not present.
        """
        if key in self._elements:
            value = self._elements.pop(key)
            if self.is_empty():
                self._key_type = None
                self._value_type = None
            return value
        return None

    def remove_value(self, key: K, value: V) -> bool:
        """Removes the entry for the specified key only if it is mapped to the specified value.
        
        Returns:
            true if the entry was removed.
        """
        if self.get(key) == value:
            self.remove(key)
            return True
        return False

    def clear(self) -> None:
        """Removes all key/value pairs from the map."""
        self._elements.clear()
        self._key_type = None
        self._value_type = None

    # Advanced mutation operations

    def get_or_put(self, key: K, default_value: Callable[[], V]) -> V:
        """Returns the value for the given key. If the key is not found, calls defaultValue and puts its result."""
        if key in self._elements:
            return self._elements[key]
        value = default_value()
        self._put_with_type_check(key, value)
        return value

    def compute(self, key: K, remapping_function: Callable[[K, Optional[V]], Optional[V]]) -> Optional[V]:
        """Attempts to compute a mapping for the specified key and its current mapped value.
        
        The remapping function receives the key and current value (or null if not present).
        If it returns null, the mapping is removed (if it was present).
        """
        current_value = self._elements.get(key)
        new_value = remapping_function(key, current_value)
        
        if new_value is None:
            if key in self._elements:
                self.remove(key)
        else:
            self._put_with_type_check(key, new_value)
        
        return new_value

    def compute_if_absent(self, key: K, mapping_function: Callable[[K], V]) -> V:
        """If the specified key is not already associated with a value, computes its value using the given function.
        
        Returns:
            The current (existing or computed) value associated with the specified key.
        """
        if key in self._elements:
            return self._elements[key]
        
        value = mapping_function(key)
        if value is not None:
            self._put_with_type_check(key, value)
        return value

    def compute_if_present(self, key: K, remapping_function: Callable[[K, V], Optional[V]]) -> Optional[V]:
        """If the value for the specified key is present, computes a new mapping.
        
        The remapping function receives the key and current value.
        If it returns null, the mapping is removed.
        """
        if key not in self._elements:
            return None
        
        current_value = self._elements[key]
        new_value = remapping_function(key, current_value)
        
        if new_value is None:
            self.remove(key)
        else:
            self._put_with_type_check(key, new_value)
        
        return new_value

    def replace(self, key: K, value: V) -> Optional[V]:
        """Replaces the entry for the specified key only if it is currently mapped to some value.
        
        Returns:
            The previous value associated with the key, or null if the key was not present.
        """
        if key in self._elements:
            return self.put(key, value)
        return None

    def replace_all(self, transform: Callable[[K, V], V]) -> None:
        """Replaces each entry's value with the result of invoking the given function on that entry."""
        for key in list(self._elements.keys()):
            current_value = self._elements[key]
            new_value = transform(key, current_value)
            self._put_with_type_check(key, new_value)

    def merge(self, key: K, value: V, remapping_function: Callable[[V, V], V]) -> V:
        """If the specified key is not already associated with a value or is associated with null, associates it with the given value.
        Otherwise, replaces the value with the results of the given remapping function.
        
        Returns:
            The new value associated with the specified key.
        """
        if key not in self._elements:
            self._put_with_type_check(key, value)
            return value
        
        old_value = self._elements[key]
        new_value = remapping_function(old_value, value)
        self._put_with_type_check(key, new_value)
        return new_value

    # Bulk operations from other maps

    def plus_assign(self, other: Dict[K, V] | 'KotMap[K, V]' | Tuple[K, V]) -> None:
        """Adds all entries from the specified map or the specified pair to this map."""
        if isinstance(other, tuple):
            key, value = other
            self.put(key, value)
        else:
            self.put_all(other)

    def minus_assign(self, key: K) -> None:
        """Removes the specified key from this map."""
        self.remove(key)

    # Python special methods for mutable operations

    def __setitem__(self, key: K, value: V) -> None:
        """Set value by key using [] operator."""
        self.put(key, value)

    def __delitem__(self, key: K) -> None:
        """Delete entry by key using del operator."""
        if key not in self._elements:
            raise KeyError(f"Key {key} not found in map")
        self.remove(key)

    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Remove specified key and return the corresponding value.
        If key is not found, default is returned if given, otherwise KeyError is raised."""
        if key in self._elements:
            return self.remove(key)
        if default is not None:
            return default
        raise KeyError(f"Key {key} not found in map")

    def popitem(self) -> Tuple[K, V]:
        """Remove and return an arbitrary (key, value) pair from the map."""
        if self.is_empty():
            raise KeyError("Map is empty")
        key, value = next(iter(self._elements.items()))
        self.remove(key)
        return key, value

    def update(self, other: Dict[K, V] | 'KotMap[K, V]' | List[Tuple[K, V]]) -> None:
        """Update the map with key/value pairs from other, overwriting existing keys."""
        self.put_all(other)

    # Override __hash__ to make it unhashable (mutable objects shouldn't be hashable)
    __hash__ = None  # type: ignore