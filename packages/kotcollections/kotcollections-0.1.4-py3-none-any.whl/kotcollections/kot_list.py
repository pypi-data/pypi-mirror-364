from __future__ import annotations

import bisect
import random as _random
from collections.abc import Iterable
from functools import reduce, cmp_to_key
from typing import TypeVar, Generic, Callable, Optional, List, Tuple, Iterator, Any, Dict, Union, TYPE_CHECKING, Set, Type

T = TypeVar('T')
R = TypeVar('R')
K = TypeVar('K')
V = TypeVar('V')

if TYPE_CHECKING:
    from kotcollections.kot_map import KotMap
    from kotcollections.kot_mutable_list import KotMutableList
    from kotcollections.kot_set import KotSet
    from kotcollections.kot_mutable_set import KotMutableSet



class KotList(Generic[T]):
    def __init__(self, elements: Optional[Iterable[T]] = None):
        self._element_type: Optional[type] = None
        if elements is None:
            self._elements: List[T] = []
        else:
            elements_list = list(elements)
            if elements_list:
                # Set the element type based on the first element
                first_elem = elements_list[0]
                if isinstance(first_elem, KotList):
                    self._element_type = KotList
                else:
                    self._element_type = type(first_elem)

                # Check all elements have the same type
                for elem in elements_list:
                    self._check_type(elem)

            self._elements = elements_list

    @classmethod
    def __class_getitem__(cls, element_type: Type[T]) -> Type['KotList[T]']:
        """Enable KotList[Type]() syntax for type specification.
        
        Example:
            animals = KotList[Animal]()
            animals_mutable = animals.to_kot_mutable_list()
            animals_mutable.add(Dog("Buddy"))
            animals_mutable.add(Cat("Whiskers"))
        """
        class TypedKotList(cls):
            def __init__(self, elements=None):
                # Only set element type if it's an actual type, not a type variable
                if isinstance(element_type, type):
                    self._element_type = element_type
                else:
                    self._element_type = None
                self._elements = []
                # Now process elements with the correct type set
                if elements is not None:
                    for elem in elements:
                        self._check_type(elem)
                        self._elements.append(elem)
        
        # Set a meaningful name for debugging
        TypedKotList.__name__ = f"{cls.__name__}[{element_type.__name__}]"
        TypedKotList.__qualname__ = f"{cls.__qualname__}[{element_type.__name__}]"
        
        return TypedKotList

    @classmethod
    def of_type(cls, element_type: Type[T], elements: Optional[Iterable[T]] = None) -> 'KotList[T]':
        """Create a KotList with a specific element type.
        
        This is useful when you want to create a list of a parent type
        but only have instances of child types.
        
        Args:
            element_type: The type of elements this list will contain
            elements: Optional initial elements
            
        Returns:
            A new KotList instance with the specified element type
            
        Example:
            animals = KotList.of_type(Animal, [Dog("Buddy"), Cat("Whiskers")])
            # or empty list
            animals = KotList.of_type(Animal)
        """
        # Use __class_getitem__ to create the same dynamic subclass
        typed_class = cls[element_type]
        return typed_class(elements)

    def _check_type(self, element: Any) -> None:
        """Check if the element has the correct type for this list."""
        # Skip type checking if element_type is a type variable or not a real type
        if self._element_type is not None and not isinstance(self._element_type, type):
            return
            
        if self._element_type is None:
            # First element sets the type
            if isinstance(element, KotList):
                self._element_type = KotList
            else:
                self._element_type = type(element)
        else:
            # Type check: allow T type or KotList type
            if isinstance(element, KotList):
                if self._element_type == KotList:
                    pass  # KotList type is allowed
                # Special handling for __class_getitem__ types (e.g., KotList[Task])
                elif (hasattr(self._element_type, '__base__') and 
                      hasattr(self._element_type, '__name__') and 
                      '[' in self._element_type.__name__ and
                      isinstance(element, self._element_type.__base__)):
                    # Check if the element has matching element type for KotList/KotSet/KotMap types
                    if hasattr(element, '_element_type') and hasattr(self._element_type, '__new__'):
                        # Extract expected element type from the __class_getitem__ type
                        # This is a more strict check for collection types
                        pass
                    else:
                        pass
                else:
                    type_name = getattr(self._element_type, '__name__', str(self._element_type))
                    raise TypeError(f"Cannot add KotList to KotList[{type_name}]")
            elif not isinstance(element, self._element_type):
                # Check if element is an instance of the expected type
                if isinstance(element, self._element_type):
                    pass  # Direct instance check passed (won't reach here, but for clarity)
                # Special handling for __class_getitem__ types
                elif (hasattr(self._element_type, '__base__') and 
                      hasattr(self._element_type, '__name__') and 
                      '[' in self._element_type.__name__ and
                      isinstance(element, self._element_type.__base__)):
                    # Allow instances of base class for __class_getitem__ types
                    pass
                else:
                    raise TypeError(
                        f"Cannot add element of type '{type(element).__name__}' to KotList[{self._element_type.__name__}]"
                    )

    def __repr__(self) -> str:
        return f"KotList({self._elements})"

    def __str__(self) -> str:
        return str(self._elements)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KotList):
            return False
        return self._elements == other._elements

    def __hash__(self) -> int:
        return hash(tuple(self._elements))

    def __iter__(self) -> Iterator[T]:
        return iter(self._elements)

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __len__(self) -> int:
        return self.size

    @property
    def size(self) -> int:
        return len(self._elements)

    @property
    def indices(self) -> range:
        return range(self.size)

    @property
    def last_index(self) -> int:
        return self.size - 1 if self.size > 0 else -1

    def is_empty(self) -> bool:
        return self.size == 0

    def is_not_empty(self) -> bool:
        return self.size > 0

    def get(self, index: int) -> T:
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of bounds for list of size {self.size}")
        return self._elements[index]

    def get_or_null(self, index: int) -> Optional[T]:
        return self._elements[index] if 0 <= index < self.size else None

    def get_or_none(self, index: int) -> Optional[T]:
        """Alias for get_or_null() - more Pythonic naming."""
        return self.get_or_null(index)

    def get_or_else(self, index: int, default_value: Callable[[int], T]) -> T:
        return self._elements[index] if 0 <= index < self.size else default_value(index)

    def first(self) -> T:
        if self.is_empty():
            raise IndexError("List is empty")
        return self._elements[0]

    def first_predicate(self, predicate: Callable[[T], bool]) -> T:
        for element in self._elements:
            if predicate(element):
                return element
        raise ValueError("No element matching predicate found")

    def first_or_null(self) -> Optional[T]:
        return self._elements[0] if self.is_not_empty() else None

    def first_or_none(self) -> Optional[T]:
        """Alias for first_or_null() - more Pythonic naming."""
        return self.first_or_null()

    def first_or_null_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        for element in self._elements:
            if predicate(element):
                return element
        return None

    def first_or_none_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Alias for first_or_null_predicate() - more Pythonic naming."""
        return self.first_or_null_predicate(predicate)

    def last(self) -> T:
        if self.is_empty():
            raise IndexError("List is empty")
        return self._elements[-1]

    def last_predicate(self, predicate: Callable[[T], bool]) -> T:
        for element in reversed(self._elements):
            if predicate(element):
                return element
        raise ValueError("No element matching predicate found")

    def last_or_null(self) -> Optional[T]:
        return self._elements[-1] if self.is_not_empty() else None

    def last_or_none(self) -> Optional[T]:
        """Alias for last_or_null() - more Pythonic naming."""
        return self.last_or_null()

    def last_or_null_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        for element in reversed(self._elements):
            if predicate(element):
                return element
        return None

    def last_or_none_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Alias for last_or_null_predicate() - more Pythonic naming."""
        return self.last_or_null_predicate(predicate)

    def element_at(self, index: int) -> T:
        return self.get(index)

    def element_at_or_else(self, index: int, default_value: Callable[[int], T]) -> T:
        return self.get_or_else(index, default_value)

    def element_at_or_null(self, index: int) -> Optional[T]:
        return self.get_or_null(index)

    def element_at_or_none(self, index: int) -> Optional[T]:
        """Alias for element_at_or_null() - more Pythonic naming."""
        return self.element_at_or_null(index)

    def contains(self, element: T) -> bool:
        return element in self._elements

    def contains_all(self, elements: Iterable[T]) -> bool:
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        if isinstance(elements, KotSet):
            elements_set = set(elements)
        elif isinstance(elements, KotMap):
            elements_set = set(elements.values)
        else:
            elements_set = set(elements)
        return all(elem in self._elements for elem in elements_set)

    def index_of(self, element: T) -> int:
        try:
            return self._elements.index(element)
        except ValueError:
            return -1

    def last_index_of(self, element: T) -> int:
        for i in range(len(self._elements) - 1, -1, -1):
            if self._elements[i] == element:
                return i
        return -1

    def index_of_first(self, predicate: Callable[[T], bool]) -> int:
        for i, element in enumerate(self._elements):
            if predicate(element):
                return i
        return -1

    def index_of_last(self, predicate: Callable[[T], bool]) -> int:
        for i in range(len(self._elements) - 1, -1, -1):
            if predicate(self._elements[i]):
                return i
        return -1

    def binary_search(self, element: T, comparator: Optional[Callable[[T, T], int]] = None) -> int:
        if comparator is None:
            index = bisect.bisect_left(self._elements, element)
            if index < len(self._elements) and self._elements[index] == element:
                return index
            return -(index + 1)
        else:
            left, right = 0, len(self._elements) - 1
            while left <= right:
                mid = (left + right) // 2
                cmp = comparator(self._elements[mid], element)
                if cmp < 0:
                    left = mid + 1
                elif cmp > 0:
                    right = mid - 1
                else:
                    return mid
            return -(left + 1)

    def binary_search_by(
        self,
        key: K,
        selector: Callable[[T], K],
        comparator: Optional[Callable[[K, K], int]] = None
    ) -> int:
        """Searches this list or its range for an element having the key returned by the specified selector function equal to the provided key value using the binary search algorithm."""
        if comparator is None:
            # Create a list of (key, index) pairs for binary search
            keys = [(selector(elem), i) for i, elem in enumerate(self._elements)]
            keys.sort(key=lambda x: x[0])
            index = bisect.bisect_left([k[0] for k in keys], key)
            if index < len(keys) and keys[index][0] == key:
                return keys[index][1]
            return -(index + 1)
        else:
            # Custom comparator case
            left, right = 0, len(self._elements) - 1
            while left <= right:
                mid = (left + right) // 2
                mid_key = selector(self._elements[mid])
                cmp = comparator(mid_key, key)
                if cmp < 0:
                    left = mid + 1
                elif cmp > 0:
                    right = mid - 1
                else:
                    return mid
            return -(left + 1)

    def map(self, transform: Callable[[T], R]) -> 'KotList[R]':
        return KotList([transform(element) for element in self._elements])

    def map_indexed(self, transform: Callable[[int, T], R]) -> 'KotList[R]':
        return KotList([transform(i, element) for i, element in enumerate(self._elements)])

    def map_not_null(self, transform: Callable[[T], Optional[R]]) -> 'KotList[R]':
        result = []
        for element in self._elements:
            transformed = transform(element)
            if transformed is not None:
                result.append(transformed)
        return KotList(result)

    def map_not_none(self, transform: Callable[[T], Optional[R]]) -> 'KotList[R]':
        """Alias for map_not_null() - more Pythonic naming."""
        return self.map_not_null(transform)

    def flat_map(self, transform: Callable[[T], Iterable[R]]) -> 'KotList[R]':
        result = []
        for element in self._elements:
            result.extend(transform(element))
        return KotList(result)

    def flatten(self) -> 'KotList[Any]':
        result = []
        for element in self._elements:
            if isinstance(element, Iterable) and not isinstance(element, (str, bytes)):
                result.extend(element)
            else:
                result.append(element)
        return KotList(result)

    def associate_with(self, value_selector: Callable[[T], V]) -> 'KotMap[T, V]':
        from kotcollections.kot_map import KotMap
        return KotMap({element: value_selector(element) for element in self._elements})

    def associate_by(self, key_selector: Callable[[T], K]) -> 'KotMap[K, T]':
        from kotcollections.kot_map import KotMap
        result = {}
        for element in self._elements:
            result[key_selector(element)] = element
        return KotMap(result)

    def associate_by_with_value(
        self, key_selector: Callable[[T], K],
        value_transform: Callable[[T], V]
    ) -> 'KotMap[K, V]':
        from kotcollections.kot_map import KotMap
        result = {}
        for element in self._elements:
            result[key_selector(element)] = value_transform(element)
        return KotMap(result)

    def filter(self, predicate: Callable[[T], bool]) -> 'KotList[T]':
        return KotList([element for element in self._elements if predicate(element)])

    def filter_indexed(self, predicate: Callable[[int, T], bool]) -> 'KotList[T]':
        return KotList([element for i, element in enumerate(self._elements) if predicate(i, element)])

    def filter_not(self, predicate: Callable[[T], bool]) -> 'KotList[T]':
        return KotList([element for element in self._elements if not predicate(element)])

    def filter_not_null(self) -> 'KotList[T]':
        return KotList([element for element in self._elements if element is not None])

    def filter_not_none(self) -> 'KotList[T]':
        """Alias for filter_not_null() - more Pythonic naming."""
        return self.filter_not_null()

    def filter_is_instance(self, klass: type) -> 'KotList[Any]':
        return KotList([element for element in self._elements if isinstance(element, klass)])

    def partition(self, predicate: Callable[[T], bool]) -> Tuple['KotList[T]', 'KotList[T]']:
        matching = []
        non_matching = []
        for element in self._elements:
            if predicate(element):
                matching.append(element)
            else:
                non_matching.append(element)
        return KotList(matching), KotList(non_matching)

    def any(self, predicate: Optional[Callable[[T], bool]] = None) -> bool:
        if predicate is None:
            return self.is_not_empty()
        return any(predicate(element) for element in self._elements)

    def all(self, predicate: Callable[[T], bool]) -> bool:
        return all(predicate(element) for element in self._elements)

    def none(self, predicate: Optional[Callable[[T], bool]] = None) -> bool:
        if predicate is None:
            return self.is_empty()
        return not any(predicate(element) for element in self._elements)

    def count(self, predicate: Optional[Callable[[T], bool]] = None) -> int:
        if predicate is None:
            return self.size
        return sum(1 for element in self._elements if predicate(element))

    def sum_of(self, selector: Callable[[T], Union[int, float]]) -> Union[int, float]:
        return sum(selector(element) for element in self._elements)

    def max_or_null(self) -> Optional[T]:
        return max(self._elements) if self.is_not_empty() else None

    def max_or_none(self) -> Optional[T]:
        """Alias for max_or_null() - more Pythonic naming."""
        return self.max_or_null()

    def min_or_null(self) -> Optional[T]:
        return min(self._elements) if self.is_not_empty() else None

    def min_or_none(self) -> Optional[T]:
        """Alias for min_or_null() - more Pythonic naming."""
        return self.min_or_null()

    def max_by_or_null(self, selector: Callable[[T], Any]) -> Optional[T]:
        if self.is_empty():
            return None
        return max(self._elements, key=selector)

    def max_by_or_none(self, selector: Callable[[T], Any]) -> Optional[T]:
        """Alias for max_by_or_null() - more Pythonic naming."""
        return self.max_by_or_null(selector)

    def min_by_or_null(self, selector: Callable[[T], Any]) -> Optional[T]:
        if self.is_empty():
            return None
        return min(self._elements, key=selector)

    def min_by_or_none(self, selector: Callable[[T], Any]) -> Optional[T]:
        """Alias for min_by_or_null() - more Pythonic naming."""
        return self.min_by_or_null(selector)

    def average(self) -> float:
        if self.is_empty():
            raise ValueError("Cannot compute average of empty list")
        return sum(self._elements) / self.size

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> 'KotList[T]':
        return KotList(sorted(self._elements, key=key, reverse=reverse))

    def sorted_descending(self) -> 'KotList[T]':
        return KotList(sorted(self._elements, reverse=True))

    def sorted_by(self, selector: Callable[[T], Any]) -> 'KotList[T]':
        return KotList(sorted(self._elements, key=selector))

    def sorted_by_descending(self, selector: Callable[[T], Any]) -> 'KotList[T]':
        return KotList(sorted(self._elements, key=selector, reverse=True))

    def sorted_with(self, comparator: Callable[[T, T], int]) -> 'KotList[T]':
        """Returns a list of all elements sorted according to the specified comparator."""
        return KotList(sorted(self._elements, key=cmp_to_key(comparator)))

    def reversed(self) -> 'KotList[T]':
        return KotList(reversed(self._elements))

    def shuffled(self, random_instance: Optional[_random.Random] = None) -> 'KotList[T]':
        elements_copy = self._elements.copy()
        if random_instance:
            random_instance.shuffle(elements_copy)
        else:
            _random.shuffle(elements_copy)
        return KotList(elements_copy)

    def group_by(self, key_selector: Callable[[T], K]) -> 'KotMap[K, KotList[T]]':
        from kotcollections.kot_map import KotMap
        result: Dict[K, List[T]] = {}
        for element in self._elements:
            key = key_selector(element)
            if key not in result:
                result[key] = []
            result[key].append(element)
        return KotMap({k: KotList(v) for k, v in result.items()})

    def group_by_with_value(
        self, key_selector: Callable[[T], K],
        value_transform: Callable[[T], V]
    ) -> 'KotMap[K, KotList[V]]':
        from kotcollections.kot_map import KotMap
        result: Dict[K, List[V]] = {}
        for element in self._elements:
            key = key_selector(element)
            if key not in result:
                result[key] = []
            result[key].append(value_transform(element))
        return KotMap({k: KotList(v) for k, v in result.items()})

    def chunked(self, size: int) -> 'KotList[KotList[T]]':
        if size <= 0:
            raise ValueError("Size must be positive")
        chunks = []
        for i in range(0, len(self._elements), size):
            chunks.append(KotList(self._elements[i:i + size]))
        return KotList(chunks)

    def chunked_transform(self, size: int, transform: Callable[['KotList[T]'], R]) -> 'KotList[R]':
        if size <= 0:
            raise ValueError("Size must be positive")
        result = []
        for i in range(0, len(self._elements), size):
            chunk = KotList(self._elements[i:i + size])
            result.append(transform(chunk))
        return KotList(result)

    def windowed(self, size: int, step: int = 1, partial_windows: bool = False) -> 'KotList[KotList[T]]':
        if size <= 0 or step <= 0:
            raise ValueError("Size and step must be positive")
        windows = []
        for i in range(0, len(self._elements), step):
            window = self._elements[i:i + size]
            if len(window) == size or (partial_windows and window):
                windows.append(KotList(window))
            elif not partial_windows and len(window) < size:
                break
        return KotList(windows)

    def distinct(self) -> 'KotList[T]':
        seen = set()
        result = []
        for element in self._elements:
            if element not in seen:
                seen.add(element)
                result.append(element)
        return KotList(result)

    def distinct_by(self, selector: Callable[[T], K]) -> 'KotList[T]':
        seen = set()
        result = []
        for element in self._elements:
            key = selector(element)
            if key not in seen:
                seen.add(key)
                result.append(element)
        return KotList(result)

    def intersect(self, other: Iterable[T]) -> 'KotList[T]':
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        if isinstance(other, KotSet):
            other_set = set(other)
        elif isinstance(other, KotMap):
            other_set = set(other.values)
        else:
            other_set = set(other)
        return KotList([element for element in self._elements if element in other_set])

    def union(self, other: Iterable[T]) -> 'KotList[T]':
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        result = list(self._elements)
        seen = set(self._elements)
        
        if isinstance(other, KotSet):
            iter_other = other
        elif isinstance(other, KotMap):
            iter_other = other.values
        else:
            iter_other = other
            
        for element in iter_other:
            if element not in seen:
                result.append(element)
                seen.add(element)
        return KotList(result)

    def plus(self, element: Union[T, Iterable[T]]) -> 'KotList[T]':
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        if isinstance(element, Iterable) and not isinstance(element, (str, bytes)):
            if isinstance(element, KotSet):
                return KotList(self._elements + list(element))
            elif isinstance(element, KotMap):
                return KotList(self._elements + list(element.values))
            else:
                return KotList(self._elements + list(element))
        else:
            return KotList(self._elements + [element])

    def minus(self, element: Union[T, Iterable[T]]) -> 'KotList[T]':
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        if isinstance(element, Iterable) and not isinstance(element, (str, bytes)):
            if isinstance(element, KotSet):
                to_remove = set(element)
            elif isinstance(element, KotMap):
                to_remove = set(element.values)
            else:
                to_remove = set(element)
            return KotList([e for e in self._elements if e not in to_remove])
        else:
            result = self._elements.copy()
            if element in result:
                result.remove(element)
            return KotList(result)

    def sub_list(self, from_index: int, to_index: int) -> 'KotList[T]':
        return KotList(self._elements[from_index:to_index])

    def zip(self, other: Iterable[R]) -> 'KotList[Tuple[T, R]]':
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        if isinstance(other, KotSet):
            return KotList(list(zip(self._elements, other)))
        elif isinstance(other, KotMap):
            return KotList(list(zip(self._elements, other.values)))
        else:
            return KotList(list(zip(self._elements, other)))

    def zip_transform(self, other: Iterable[R], transform: Callable[[T, R], V]) -> 'KotList[V]':
        # Support KotSet and KotMap explicitly
        from kotcollections.kot_set import KotSet
        from kotcollections.kot_map import KotMap
        
        if isinstance(other, KotSet):
            iter_other = other
        elif isinstance(other, KotMap):
            iter_other = other.values
        else:
            iter_other = other
        
        return KotList([transform(a, b) for a, b in zip(self._elements, iter_other)])

    def unzip(self) -> Tuple['KotList[Any]', 'KotList[Any]']:
        if self.is_empty():
            return KotList(), KotList()
        first_elements = []
        second_elements = []
        for pair in self._elements:
            first_elements.append(pair[0])
            second_elements.append(pair[1])
        return KotList(first_elements), KotList(second_elements)

    def fold(self, initial: R, operation: Callable[[R, T], R]) -> R:
        result = initial
        for element in self._elements:
            result = operation(result, element)
        return result

    def reduce(self, operation: Callable[[T, T], T]) -> T:
        if self.is_empty():
            raise ValueError("Cannot reduce empty list")
        return reduce(operation, self._elements)

    def scan(self, initial: R, operation: Callable[[R, T], R]) -> 'KotList[R]':
        result = [initial]
        acc = initial
        for element in self._elements:
            acc = operation(acc, element)
            result.append(acc)
        return KotList(result)

    def for_each(self, action: Callable[[T], None]) -> None:
        for element in self._elements:
            action(element)

    def for_each_indexed(self, action: Callable[[int, T], None]) -> None:
        for i, element in enumerate(self._elements):
            action(i, element)

    def on_each(self, action: Callable[[T], None]) -> 'KotList[T]':
        for element in self._elements:
            action(element)
        return self

    def to_list(self) -> List[T]:
        return self._elements.copy()

    def to_set(self) -> Set[T]:
        return set(self._elements.copy())

    def to_kot_list(self) -> 'KotList[T]':
        # Preserve type information when converting
        if self._element_type is not None:
            return KotList.of_type(self._element_type, self._elements.copy())
        else:
            return KotList(self._elements.copy())

    def to_kot_mutable_list(self) -> 'KotMutableList[T]':
        from kotcollections.kot_mutable_list import KotMutableList
        # Preserve type information when converting
        if self._element_type is not None:
            mutable_list = KotMutableList.of_type(self._element_type, self._elements.copy())
        else:
            mutable_list = KotMutableList(self._elements.copy())
        return mutable_list

    def to_kot_set(self) -> 'KotSet[T]':
        from kotcollections.kot_set import KotSet
        # Preserve type information when converting
        if self._element_type is not None:
            return KotSet.of_type(self._element_type, self._elements.copy())
        else:
            return KotSet(self._elements.copy())

    def to_kot_mutable_set(self) -> 'KotMutableSet[T]':
        from kotcollections.kot_mutable_set import KotMutableSet
        # Preserve type information when converting
        if self._element_type is not None:
            return KotMutableSet.of_type(self._element_type, self._elements.copy())
        else:
            return KotMutableSet(self._elements.copy())

    def join_to_string(
        self, separator: str = ", ", prefix: str = "", postfix: str = "",
        limit: int = -1, truncated: str = "...",
        transform: Optional[Callable[[T], str]] = None
    ) -> str:
        if transform is None:
            transform = str

        result = prefix
        count = 0

        for i, element in enumerate(self._elements):
            if limit >= 0 and count >= limit:
                result += truncated
                break

            if i > 0:
                result += separator

            result += transform(element)
            count += 1

        result += postfix
        return result

    # Element retrieval methods
    def component1(self) -> T:
        """Returns the first element (for destructuring declarations)."""
        return self.get(0)

    def component2(self) -> T:
        """Returns the second element (for destructuring declarations)."""
        return self.get(1)

    def component3(self) -> T:
        """Returns the third element (for destructuring declarations)."""
        return self.get(2)

    def component4(self) -> T:
        """Returns the fourth element (for destructuring declarations)."""
        return self.get(3)

    def component5(self) -> T:
        """Returns the fifth element (for destructuring declarations)."""
        return self.get(4)

    def single(self) -> T:
        """Returns the single element, or throws an exception if the list is empty or has more than one element."""
        if self.size == 0:
            raise ValueError("List is empty")
        if self.size > 1:
            raise ValueError("List has more than one element")
        return self._elements[0]

    def single_or_null(self) -> Optional[T]:
        """Returns the single element, or null if the list is empty or has more than one element."""
        return self._elements[0] if self.size == 1 else None

    def single_or_none(self) -> Optional[T]:
        """Alias for single_or_null() - more Pythonic naming."""
        return self.single_or_null()

    def single_predicate(self, predicate: Callable[[T], bool]) -> T:
        """Returns the single element matching the given predicate, or throws exception if there is no or more than one matching element."""
        found = None
        found_multiple = False

        for element in self._elements:
            if predicate(element):
                if found is not None:
                    found_multiple = True
                    break
                found = element

        if found is None:
            raise ValueError("No element matching predicate found")
        if found_multiple:
            raise ValueError("More than one element matching predicate found")

        return found

    def single_or_null_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Returns the single element matching the given predicate, or null if element was not found or more than one element was found."""
        found = None

        for element in self._elements:
            if predicate(element):
                if found is not None:
                    return None
                found = element

        return found

    def single_or_none_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Alias for single_or_null_predicate() - more Pythonic naming."""
        return self.single_or_null_predicate(predicate)

    def random(self, random_instance: Optional[_random.Random] = None) -> T:
        """Returns a random element from this list."""
        if self.is_empty():
            raise IndexError("List is empty")
        if random_instance:
            return random_instance.choice(self._elements)
        return _random.choice(self._elements)

    def random_or_null(self, random_instance: Optional[_random.Random] = None) -> Optional[T]:
        """Returns a random element from this list, or null if this list is empty."""
        if self.is_empty():
            return None
        if random_instance:
            return random_instance.choice(self._elements)
        return _random.choice(self._elements)

    def random_or_none(self, random_instance: Optional[_random.Random] = None) -> Optional[T]:
        """Alias for random_or_null() - more Pythonic naming."""
        return self.random_or_null(random_instance)

    # Sublist retrieval methods
    def slice(self, indices: Iterable[int]) -> 'KotList[T]':
        """Returns a list containing elements at specified indices."""
        result = []
        for index in indices:
            if 0 <= index < self.size:
                result.append(self._elements[index])
            else:
                raise IndexError(f"Index {index} out of bounds for list of size {self.size}")
        return KotList(result)

    def take(self, n: int) -> 'KotList[T]':
        """Returns a list containing first n elements."""
        if n < 0:
            raise ValueError("Requested element count is less than zero")
        return KotList(self._elements[:n])

    def take_last(self, n: int) -> 'KotList[T]':
        """Returns a list containing last n elements."""
        if n < 0:
            raise ValueError("Requested element count is less than zero")
        if n == 0:
            return KotList()
        return KotList(self._elements[-n:])

    def take_while(self, predicate: Callable[[T], bool]) -> 'KotList[T]':
        """Returns a list containing first elements satisfying the given predicate."""
        result = []
        for element in self._elements:
            if predicate(element):
                result.append(element)
            else:
                break
        return KotList(result)

    def take_last_while(self, predicate: Callable[[T], bool]) -> 'KotList[T]':
        """Returns a list containing last elements satisfying the given predicate."""
        result = []
        for element in reversed(self._elements):
            if predicate(element):
                result.append(element)
            else:
                break
        return KotList(reversed(result))

    def drop(self, n: int) -> 'KotList[T]':
        """Returns a list containing all elements except first n elements."""
        if n < 0:
            raise ValueError("Requested element count is less than zero")
        return KotList(self._elements[n:])

    def drop_last(self, n: int) -> 'KotList[T]':
        """Returns a list containing all elements except last n elements."""
        if n < 0:
            raise ValueError("Requested element count is less than zero")
        if n == 0:
            return KotList(self._elements)
        return KotList(self._elements[:-n])

    def drop_while(self, predicate: Callable[[T], bool]) -> 'KotList[T]':
        """Returns a list containing all elements except first elements that satisfy the given predicate."""
        index = 0
        for i, element in enumerate(self._elements):
            if not predicate(element):
                index = i
                break
        else:
            return KotList()
        return KotList(self._elements[index:])

    def drop_last_while(self, predicate: Callable[[T], bool]) -> 'KotList[T]':
        """Returns a list containing all elements except last elements that satisfy the given predicate."""
        index = len(self._elements)
        for i in range(len(self._elements) - 1, -1, -1):
            if not predicate(self._elements[i]):
                index = i + 1
                break
        else:
            return KotList()
        return KotList(self._elements[:index])

    # Transformation methods
    def map_indexed_not_null(self, transform: Callable[[int, T], Optional[R]]) -> 'KotList[R]':
        """Returns a list containing only the non-null results of applying the given transform function to each element and its index."""
        result = []
        for i, element in enumerate(self._elements):
            transformed = transform(i, element)
            if transformed is not None:
                result.append(transformed)
        return KotList(result)

    def map_indexed_not_none(self, transform: Callable[[int, T], Optional[R]]) -> 'KotList[R]':
        """Alias for map_indexed_not_null() - more Pythonic naming."""
        return self.map_indexed_not_null(transform)

    def flat_map_indexed(self, transform: Callable[[int, T], Iterable[R]]) -> 'KotList[R]':
        """Returns a single list of all elements yielded from results of transform function being invoked on each element and its index."""
        result = []
        for i, element in enumerate(self._elements):
            result.extend(transform(i, element))
        return KotList(result)

    def zip_with_next(self) -> 'KotList[Tuple[T, T]]':
        """Returns a list of pairs of each two adjacent elements in this list."""
        if self.size < 2:
            return KotList()
        result = []
        for i in range(self.size - 1):
            result.append((self._elements[i], self._elements[i + 1]))
        return KotList(result)

    def zip_with_next_transform(self, transform: Callable[[T, T], R]) -> 'KotList[R]':
        """Returns a list containing the results of applying the given transform function to each pair of two adjacent elements."""
        if self.size < 2:
            return KotList()
        result = []
        for i in range(self.size - 1):
            result.append(transform(self._elements[i], self._elements[i + 1]))
        return KotList(result)

    # Search methods
    def find(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Returns the first element matching the given predicate, or null if no such element was found."""
        return self.first_or_null_predicate(predicate)

    def find_last(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Returns the last element matching the given predicate, or null if no such element was found."""
        return self.last_or_null_predicate(predicate)

    def first_not_null_of(self, transform: Callable[[T], Optional[R]]) -> R:
        """Returns the first non-null value produced by transform function or throws NoSuchElementException."""
        for element in self._elements:
            result = transform(element)
            if result is not None:
                return result
        raise ValueError("No non-null value found")

    def first_not_null_of_or_null(self, transform: Callable[[T], Optional[R]]) -> Optional[R]:
        """Returns the first non-null value produced by transform function or null."""
        for element in self._elements:
            result = transform(element)
            if result is not None:
                return result
        return None

    def first_not_none_of(self, transform: Callable[[T], Optional[R]]) -> R:
        """Alias for first_not_null_of() - more Pythonic naming."""
        return self.first_not_null_of(transform)

    def first_not_none_of_or_none(self, transform: Callable[[T], Optional[R]]) -> Optional[R]:
        """Alias for first_not_null_of_or_null() - more Pythonic naming."""
        return self.first_not_null_of_or_null(transform)

    # Aggregation methods
    def max_by(self, selector: Callable[[T], Any]) -> T:
        """Returns the first element yielding the largest value of the given function."""
        if self.is_empty():
            raise ValueError("Cannot find max of empty list")
        return max(self._elements, key=selector)

    def min_by(self, selector: Callable[[T], Any]) -> T:
        """Returns the first element yielding the smallest value of the given function."""
        if self.is_empty():
            raise ValueError("Cannot find min of empty list")
        return min(self._elements, key=selector)

    def max_of(self, selector: Callable[[T], Any]) -> Any:
        """Returns the largest value among all values produced by selector function."""
        if self.is_empty():
            raise ValueError("Cannot find max of empty list")
        return max(selector(element) for element in self._elements)

    def min_of(self, selector: Callable[[T], Any]) -> Any:
        """Returns the smallest value among all values produced by selector function."""
        if self.is_empty():
            raise ValueError("Cannot find min of empty list")
        return min(selector(element) for element in self._elements)

    def max_of_or_null(self, selector: Callable[[T], Any]) -> Optional[Any]:
        """Returns the largest value among all values produced by selector function or null if there are no elements."""
        if self.is_empty():
            return None
        return max(selector(element) for element in self._elements)

    def max_of_or_none(self, selector: Callable[[T], Any]) -> Optional[Any]:
        """Alias for max_of_or_null() - more Pythonic naming."""
        return self.max_of_or_null(selector)

    def min_of_or_null(self, selector: Callable[[T], Any]) -> Optional[Any]:
        """Returns the smallest value among all values produced by selector function or null if there are no elements."""
        if self.is_empty():
            return None
        return min(selector(element) for element in self._elements)

    def min_of_or_none(self, selector: Callable[[T], Any]) -> Optional[Any]:
        """Alias for min_of_or_null() - more Pythonic naming."""
        return self.min_of_or_null(selector)

    def max_of_with(self, comparator: Callable[[Any, Any], int], selector: Callable[[T], Any]) -> Any:
        """Returns the largest value according to the provided comparator among all values produced by selector function."""
        if self.is_empty():
            raise ValueError("Cannot find max of empty list")
        values = [selector(element) for element in self._elements]
        # Python doesn't have cmp parameter in max/min, so we need to use a different approach
        result = values[0]
        for value in values[1:]:
            if comparator(value, result) > 0:
                result = value
        return result

    def min_of_with(self, comparator: Callable[[Any, Any], int], selector: Callable[[T], Any]) -> Any:
        """Returns the smallest value according to the provided comparator among all values produced by selector function."""
        if self.is_empty():
            raise ValueError("Cannot find min of empty list")
        values = [selector(element) for element in self._elements]
        # Python doesn't have cmp parameter in max/min, so we need to use a different approach
        result = values[0]
        for value in values[1:]:
            if comparator(value, result) < 0:
                result = value
        return result

    def max_of_with_or_null(self, comparator: Callable[[Any, Any], int], selector: Callable[[T], Any]) -> Optional[Any]:
        """Returns the largest value according to the provided comparator among all values produced by selector function or null."""
        if self.is_empty():
            return None
        values = [selector(element) for element in self._elements]
        # Python doesn't have cmp parameter in max/min, so we need to use a different approach
        result = values[0]
        for value in values[1:]:
            if comparator(value, result) > 0:
                result = value
        return result

    def max_of_with_or_none(self, comparator: Callable[[Any, Any], int], selector: Callable[[T], Any]) -> Optional[Any]:
        """Alias for max_of_with_or_null() - more Pythonic naming."""
        return self.max_of_with_or_null(comparator, selector)

    def min_of_with_or_null(self, comparator: Callable[[Any, Any], int], selector: Callable[[T], Any]) -> Optional[Any]:
        """Returns the smallest value according to the provided comparator among all values produced by selector function or null."""
        if self.is_empty():
            return None
        values = [selector(element) for element in self._elements]
        # Python doesn't have cmp parameter in max/min, so we need to use a different approach
        result = values[0]
        for value in values[1:]:
            if comparator(value, result) < 0:
                result = value
        return result

    def min_of_with_or_none(self, comparator: Callable[[Any, Any], int], selector: Callable[[T], Any]) -> Optional[Any]:
        """Alias for min_of_with_or_null() - more Pythonic naming."""
        return self.min_of_with_or_null(comparator, selector)

    # Fold/Reduce variations
    def fold_indexed(self, initial: R, operation: Callable[[int, R, T], R]) -> R:
        """Accumulates value starting with initial value and applying operation from left to right to current accumulator value and each element with its index."""
        result = initial
        for i, element in enumerate(self._elements):
            result = operation(i, result, element)
        return result

    def fold_right(self, initial: R, operation: Callable[[T, R], R]) -> R:
        """Accumulates value starting with initial value and applying operation from right to left to each element and current accumulator value."""
        result = initial
        for element in reversed(self._elements):
            result = operation(element, result)
        return result

    def fold_right_indexed(self, initial: R, operation: Callable[[int, T, R], R]) -> R:
        """Accumulates value starting with initial value and applying operation from right to left to each element with its index and current accumulator value."""
        result = initial
        for i in range(len(self._elements) - 1, -1, -1):
            result = operation(i, self._elements[i], result)
        return result

    def reduce_indexed(self, operation: Callable[[int, T, T], T]) -> T:
        """Accumulates value starting with the first element and applying operation from left to right to current accumulator value and each element with its index."""
        if self.is_empty():
            raise ValueError("Cannot reduce empty list")
        result = self._elements[0]
        for i in range(1, len(self._elements)):
            result = operation(i, result, self._elements[i])
        return result

    def reduce_right(self, operation: Callable[[T, T], T]) -> T:
        """Accumulates value starting with the last element and applying operation from right to left to each element and current accumulator value."""
        if self.is_empty():
            raise ValueError("Cannot reduce empty list")
        result = self._elements[-1]
        for i in range(len(self._elements) - 2, -1, -1):
            result = operation(self._elements[i], result)
        return result

    def reduce_right_indexed(self, operation: Callable[[int, T, T], T]) -> T:
        """Accumulates value starting with the last element and applying operation from right to left to each element with its index and current accumulator value."""
        if self.is_empty():
            raise ValueError("Cannot reduce empty list")
        result = self._elements[-1]
        for i in range(len(self._elements) - 2, -1, -1):
            result = operation(i, self._elements[i], result)
        return result

    def reduce_indexed_or_null(self, operation: Callable[[int, T, T], T]) -> Optional[T]:
        """Accumulates value starting with the first element and applying operation from left to right, or null if the list is empty."""
        if self.is_empty():
            return None
        return self.reduce_indexed(operation)

    def reduce_indexed_or_none(self, operation: Callable[[int, T, T], T]) -> Optional[T]:
        """Alias for reduce_indexed_or_null() - more Pythonic naming."""
        return self.reduce_indexed_or_null(operation)

    def reduce_right_or_null(self, operation: Callable[[T, T], T]) -> Optional[T]:
        """Accumulates value starting with the last element and applying operation from right to left, or null if the list is empty."""
        if self.is_empty():
            return None
        return self.reduce_right(operation)

    def reduce_right_or_none(self, operation: Callable[[T, T], T]) -> Optional[T]:
        """Alias for reduce_right_or_null() - more Pythonic naming."""
        return self.reduce_right_or_null(operation)

    def reduce_right_indexed_or_null(self, operation: Callable[[int, T, T], T]) -> Optional[T]:
        """Accumulates value starting with the last element and applying operation from right to left with indices, or null if the list is empty."""
        if self.is_empty():
            return None
        return self.reduce_right_indexed(operation)

    def reduce_right_indexed_or_none(self, operation: Callable[[int, T, T], T]) -> Optional[T]:
        """Alias for reduce_right_indexed_or_null() - more Pythonic naming."""
        return self.reduce_right_indexed_or_null(operation)

    def reduce_or_null(self, operation: Callable[[T, T], T]) -> Optional[T]:
        """Accumulates value starting with the first element and applying operation from left to right, or null if the list is empty."""
        if self.is_empty():
            return None
        return self.reduce(operation)

    def reduce_or_none(self, operation: Callable[[T, T], T]) -> Optional[T]:
        """Alias for reduce_or_null() - more Pythonic naming."""
        return self.reduce_or_null(operation)

    def running_fold(self, initial: R, operation: Callable[[R, T], R]) -> 'KotList[R]':
        """Returns a list containing successive accumulation values generated by applying operation from left to right."""
        # This is the same as scan, which is already implemented
        return self.scan(initial, operation)

    def running_fold_indexed(self, initial: R, operation: Callable[[int, R, T], R]) -> 'KotList[R]':
        """Returns a list containing successive accumulation values generated by applying operation from left to right with indices."""
        result = [initial]
        acc = initial
        for i, element in enumerate(self._elements):
            acc = operation(i, acc, element)
            result.append(acc)
        return KotList(result)

    def scan_indexed(self, initial: R, operation: Callable[[int, R, T], R]) -> 'KotList[R]':
        """Returns a list containing successive accumulation values generated by applying operation from left to right with indices."""
        return self.running_fold_indexed(initial, operation)

    def running_reduce(self, operation: Callable[[T, T], T]) -> 'KotList[T]':
        """Returns a list containing successive accumulation values generated by applying operation from left to right."""
        if self.is_empty():
            return KotList()
        result = [self._elements[0]]
        acc = self._elements[0]
        for element in self._elements[1:]:
            acc = operation(acc, element)
            result.append(acc)
        return KotList(result)

    def running_reduce_indexed(self, operation: Callable[[int, T, T], T]) -> 'KotList[T]':
        """Returns a list containing successive accumulation values generated by applying operation from left to right with indices."""
        if self.is_empty():
            return KotList()
        result = [self._elements[0]]
        acc = self._elements[0]
        for i in range(1, len(self._elements)):
            acc = operation(i, acc, self._elements[i])
            result.append(acc)
        return KotList(result)

    # Other methods
    def as_reversed(self) -> 'KotList[T]':
        """Returns a reversed read-only view of the original List."""
        # In Python, we'll return a new KotList with reversed elements
        # since we don't have true "view" semantics like Kotlin
        return self.reversed()

    def as_sequence(self) -> Iterator[T]:
        """Creates a Sequence instance that wraps the original list."""
        # In Python, we'll return an iterator
        return iter(self._elements)

    def with_index(self) -> Iterator[Tuple[int, T]]:
        """Returns a lazy Iterable of IndexedValue for each element of the original list."""
        return enumerate(self._elements)

    def on_each_indexed(self, action: Callable[[int, T], None]) -> 'KotList[T]':
        """Performs the given action on each element with its index, returning the list itself afterwards."""
        for i, element in enumerate(self._elements):
            action(i, element)
        return self

    def if_empty(self, default_value: Callable[[], 'KotList[T]']) -> 'KotList[T]':
        """Returns this list if it's not empty or the result of calling defaultValue function if the list is empty."""
        return self if self.is_not_empty() else default_value()

    # ListIterator methods
    def list_iterator(self, index: int = 0) -> Iterator[T]:
        """Returns a list iterator over the elements in this list."""
        if index < 0 or index > self.size:
            raise IndexError(f"Index {index} out of bounds for list of size {self.size}")
        return iter(self._elements[index:])

    # Operator overloads
    def __add__(self, other: Union[T, Iterable[T]]) -> 'KotList[T]':
        """Overload + operator for plus() method."""
        return self.plus(other)

    def __sub__(self, other: Union[T, Iterable[T]]) -> 'KotList[T]':
        """Overload - operator for minus() method."""
        return self.minus(other)
