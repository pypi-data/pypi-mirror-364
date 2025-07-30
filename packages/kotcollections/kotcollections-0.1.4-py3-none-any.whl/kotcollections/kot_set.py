"""
KotSet: A Python implementation of Kotlin's Set interface with snake_case naming convention.
"""

from __future__ import annotations

from collections import defaultdict
from functools import reduce
from typing import TypeVar, Generic, Callable, Optional, Set, Iterator, Any, Tuple, List, Type, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from kotcollections.kot_list import KotList
    from kotcollections.kot_mutable_list import KotMutableList
    from kotcollections.kot_map import KotMap
    from kotcollections.kot_mutable_set import KotMutableSet

T = TypeVar('T')
R = TypeVar('R')



class KotSet(Generic[T]):
    """A Python implementation of Kotlin's Set interface.
    
    This class provides all methods from Kotlin's Set interface with snake_case naming,
    maintaining type safety and immutability.
    """

    def __init__(self, elements: Optional[Set[T] | List[T] | Iterator[T] | 'KotList[T]' | 'KotMutableList[T]'] = None):
        """Initialize a KotSet with optional elements.
        
        Args:
            elements: Initial elements for the set (set, list, iterator, KotList, or KotMutableList)
        """
        self._elements: Set[T] = set()
        self._element_type: Optional[type] = None

        if elements is not None:
            # Check for KotList/KotMutableList first to avoid circular imports
            if hasattr(elements, '_elements') and hasattr(elements, 'to_list'):
                # It's a KotList or KotMutableList
                for element in elements:
                    self._add_with_type_check(element)
            elif isinstance(elements, set):
                for element in elements:
                    self._add_with_type_check(element)
            elif isinstance(elements, list):
                for element in elements:
                    self._add_with_type_check(element)
            else:  # Iterator
                for element in elements:
                    self._add_with_type_check(element)

    @classmethod
    def __class_getitem__(cls, element_type: Type[T]) -> Type['KotSet[T]']:
        """Enable KotSet[Type]() syntax for type specification.
        
        Example:
            animals = KotSet[Animal]()
            animals.add(Dog("Buddy"))
            animals.add(Cat("Whiskers"))
        """
        class TypedKotSet(cls):
            def __init__(self, elements=None):
                # Only set element type if it's an actual type, not a type variable
                if isinstance(element_type, type):
                    self._element_type = element_type
                else:
                    self._element_type = None
                self._elements = set()
                # Now process elements with the correct type set
                if elements is not None:
                    if hasattr(elements, '_elements') and hasattr(elements, 'to_list'):
                        # It's a KotList or KotMutableList
                        for element in elements:
                            self._add_with_type_check(element)
                    elif isinstance(elements, set):
                        for element in elements:
                            self._add_with_type_check(element)
                    elif isinstance(elements, list):
                        for element in elements:
                            self._add_with_type_check(element)
                    else:  # Iterator
                        for element in elements:
                            self._add_with_type_check(element)
        
        # Set a meaningful name for debugging
        TypedKotSet.__name__ = f"{cls.__name__}[{element_type.__name__}]"
        TypedKotSet.__qualname__ = f"{cls.__qualname__}[{element_type.__name__}]"
        
        return TypedKotSet

    @classmethod
    def of_type(cls, element_type: Type[T], elements: Optional[Set[T] | List[T] | Iterator[T]] = None) -> 'KotSet[T]':
        """Create a KotSet with a specific element type.
        
        This is useful when you want to create a set of a parent type
        but only have instances of child types.
        
        Args:
            element_type: The type of elements this set will contain
            elements: Optional initial elements
            
        Returns:
            A new KotSet instance with the specified element type
            
        Example:
            animals = KotSet.of_type(Animal, [Dog("Buddy"), Cat("Whiskers")])
            # or empty set
            animals = KotSet.of_type(Animal)
            animals.add(Dog("Max"))
        """
        # Use __class_getitem__ to create the same dynamic subclass
        typed_class = cls[element_type]
        return typed_class(elements)

    def _add_with_type_check(self, element: T) -> None:
        """Add an element with type checking."""
        # Skip type checking if element_type is a type variable or not a real type
        if self._element_type is not None and not isinstance(self._element_type, type):
            self._elements.add(element)
            return
            
        if self._element_type is None and element is not None:
            self._element_type = type(element) if not isinstance(element, KotSet) else KotSet

        if element is not None and self._element_type is not None:
            if isinstance(element, KotSet) and self._element_type == KotSet:
                self._elements.add(element)
            elif not isinstance(element, KotSet):
                # Check if element is an instance of the expected type
                if isinstance(element, self._element_type):
                    self._elements.add(element)
                # Special handling for __class_getitem__ types (e.g., KotList[Holiday])
                elif (hasattr(self._element_type, '__base__') and 
                      hasattr(self._element_type, '__name__') and 
                      '[' in self._element_type.__name__ and
                      isinstance(element, self._element_type.__base__)):
                    # Check if the element has matching element type for KotList/KotSet/KotMap types
                    if hasattr(element, '_element_type') and hasattr(self._element_type, '__new__'):
                        # Extract expected element type from the __class_getitem__ type
                        # This is a more strict check for collection types
                        self._elements.add(element)
                    else:
                        self._elements.add(element)
                else:
                    raise TypeError(
                        f"All elements must be of type {self._element_type.__name__}, got {type(element).__name__}"
                    )
            else:
                self._elements.add(element)
        elif element is None:
            self._elements.add(element)

    # Basic Set operations

    def is_empty(self) -> bool:
        """Returns true if the set is empty."""
        return len(self._elements) == 0

    def is_not_empty(self) -> bool:
        """Returns true if the set is not empty."""
        return len(self._elements) > 0

    @property
    def size(self) -> int:
        """Returns the size of the set."""
        return len(self._elements)

    def contains(self, element: T) -> bool:
        """Returns true if the set contains the specified element."""
        return element in self._elements

    def contains_all(self, elements: Set[T] | List[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> bool:
        """Returns true if the set contains all of the elements in the specified collection."""
        if isinstance(elements, KotSet):
            elements = elements._elements
        elif hasattr(elements, '_elements') and hasattr(elements, 'to_list'):
            # It's a KotList or KotMutableList
            elements = set(elements)
        elif isinstance(elements, list):
            elements = set(elements)
        return elements.issubset(self._elements)

    # Access operations

    def first(self) -> T:
        """Returns the first element."""
        if self.is_empty():
            raise ValueError("Set is empty")
        return next(iter(self._elements))

    def first_or_null(self) -> Optional[T]:
        """Returns the first element, or null if the set is empty."""
        if self.is_empty():
            return None
        return next(iter(self._elements))

    def first_or_none(self) -> Optional[T]:
        """Pythonic alias for first_or_null()."""
        return self.first_or_null()

    def first_predicate(self, predicate: Callable[[T], bool]) -> T:
        """Returns the first element matching the given predicate."""
        for element in self._elements:
            if predicate(element):
                return element
        raise ValueError("No element matching predicate")

    def first_or_null_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Returns the first element matching the given predicate, or null if not found."""
        for element in self._elements:
            if predicate(element):
                return element
        return None

    def first_or_none_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Pythonic alias for first_or_null_predicate()."""
        return self.first_or_null_predicate(predicate)

    def last(self) -> T:
        """Returns the last element."""
        if self.is_empty():
            raise ValueError("Set is empty")
        return list(self._elements)[-1]

    def last_or_null(self) -> Optional[T]:
        """Returns the last element, or null if the set is empty."""
        if self.is_empty():
            return None
        return list(self._elements)[-1]

    def last_or_none(self) -> Optional[T]:
        """Pythonic alias for last_or_null()."""
        return self.last_or_null()

    def single(self) -> T:
        """Returns the single element, or throws an exception if the set is empty or has more than one element."""
        if self.size == 0:
            raise ValueError("Set is empty")
        if self.size > 1:
            raise ValueError("Set has more than one element")
        return next(iter(self._elements))

    def single_or_null(self) -> Optional[T]:
        """Returns the single element, or null if the set is empty or has more than one element."""
        if self.size != 1:
            return None
        return next(iter(self._elements))

    def single_or_none(self) -> Optional[T]:
        """Pythonic alias for single_or_null()."""
        return self.single_or_null()

    def single_predicate(self, predicate: Callable[[T], bool]) -> T:
        """Returns the single element matching the given predicate."""
        matches = [e for e in self._elements if predicate(e)]
        if len(matches) == 0:
            raise ValueError("No element matching predicate")
        if len(matches) > 1:
            raise ValueError("More than one element matching predicate")
        return matches[0]

    def single_or_null_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Returns the single element matching the given predicate, or null."""
        matches = [e for e in self._elements if predicate(e)]
        if len(matches) != 1:
            return None
        return matches[0]

    def single_or_none_predicate(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Pythonic alias for single_or_null_predicate()."""
        return self.single_or_null_predicate(predicate)

    # Transformation operations

    def map(self, transform: Callable[[T], R]) -> 'KotSet[R]':
        """Returns a set containing the results of applying the given transform function to each element."""
        return KotSet(transform(element) for element in self._elements)

    def map_not_null(self, transform: Callable[[T], Optional[R]]) -> 'KotSet[R]':
        """Returns a set containing only the non-null results of applying the given transform function."""
        result = []
        for element in self._elements:
            transformed = transform(element)
            if transformed is not None:
                result.append(transformed)
        return KotSet(result)

    def map_not_none(self, transform: Callable[[T], Optional[R]]) -> 'KotSet[R]':
        """Pythonic alias for map_not_null()."""
        return self.map_not_null(transform)

    def flat_map(
        self,
        transform: Callable[[T], Set[R] | List[R] | 'KotSet[R]' | 'KotList[R]' | 'KotMutableList[R]']
    ) -> 'KotSet[R]':
        """Returns a single set of all elements from results of transform function."""
        result = []
        for element in self._elements:
            transformed = transform(element)
            if isinstance(transformed, KotSet):
                result.extend(transformed._elements)
            elif hasattr(transformed, '_elements') and hasattr(transformed, 'to_list'):
                # It's a KotList or KotMutableList
                result.extend(transformed)
            elif isinstance(transformed, set):
                result.extend(transformed)
            else:  # List
                result.extend(transformed)
        return KotSet(result)

    def map_indexed(self, transform: Callable[[int, T], R]) -> 'KotSet[R]':
        """Returns a set containing the results of applying the given transform function to each element and its index."""
        return KotSet(transform(index, element) for index, element in enumerate(self._elements))

    def flat_map_indexed(
        self,
        transform: Callable[[int, T], Set[R] | List[R] | 'KotSet[R]' | 'KotList[R]' | 'KotMutableList[R]']
    ) -> 'KotSet[R]':
        """Returns a single set of all elements from results of transform function applied to each element and its index."""
        result = []
        for index, element in enumerate(self._elements):
            transformed = transform(index, element)
            if isinstance(transformed, KotSet):
                result.extend(transformed._elements)
            elif hasattr(transformed, '_elements') and hasattr(transformed, 'to_list'):
                # It's a KotList or KotMutableList
                result.extend(transformed)
            elif isinstance(transformed, set):
                result.extend(transformed)
            else:  # List
                result.extend(transformed)
        return KotSet(result)

    # Filtering operations

    def filter(self, predicate: Callable[[T], bool]) -> 'KotSet[T]':
        """Returns a set containing only elements matching the given predicate."""
        return KotSet(element for element in self._elements if predicate(element))

    def filter_not(self, predicate: Callable[[T], bool]) -> 'KotSet[T]':
        """Returns a set containing only elements not matching the given predicate."""
        return KotSet(element for element in self._elements if not predicate(element))

    def filter_not_null(self) -> 'KotSet[T]':
        """Returns a set containing all elements that are not null."""
        return KotSet(element for element in self._elements if element is not None)

    def filter_not_none(self) -> 'KotSet[T]':
        """Pythonic alias for filter_not_null()."""
        return self.filter_not_null()

    def filter_is_instance(self, klass: Type[R]) -> 'KotSet[R]':
        """Returns a set containing all elements that are instances of the specified class."""
        return KotSet(element for element in self._elements if isinstance(element, klass))

    # Aggregation operations

    def all(self, predicate: Callable[[T], bool]) -> bool:
        """Returns true if all elements match the given predicate."""
        return all(predicate(element) for element in self._elements)

    def none(self, predicate: Callable[[T], bool]) -> bool:
        """Returns true if no elements match the given predicate."""
        return not any(predicate(element) for element in self._elements)

    def any(self, predicate: Optional[Callable[[T], bool]] = None) -> bool:
        """Returns true if set has at least one element, or any element matches the predicate."""
        if predicate is None:
            return self.is_not_empty()
        return any(predicate(element) for element in self._elements)

    def count(self, predicate: Optional[Callable[[T], bool]] = None) -> int:
        """Returns the number of elements matching the given predicate."""
        if predicate is None:
            return self.size
        return sum(1 for element in self._elements if predicate(element))

    def sum_of(self, selector: Callable[[T], float | int]) -> float | int:
        """Returns the sum of all values produced by selector function."""
        if self.is_empty():
            return 0
        values = [selector(element) for element in self._elements]
        return sum(values)

    def average(self, selector: Callable[[T], float | int]) -> float:
        """Returns the average of all values produced by selector function."""
        if self.is_empty():
            raise ValueError("Set is empty")
        values = [selector(element) for element in self._elements]
        return sum(values) / len(values)

    def max_or_null(self) -> Optional[T]:
        """Returns the largest element or null if there are no elements."""
        if self.is_empty():
            return None
        return max(self._elements)

    def max_or_none(self) -> Optional[T]:
        """Pythonic alias for max_or_null()."""
        return self.max_or_null()

    def min_or_null(self) -> Optional[T]:
        """Returns the smallest element or null if there are no elements."""
        if self.is_empty():
            return None
        return min(self._elements)

    def min_or_none(self) -> Optional[T]:
        """Pythonic alias for min_or_null()."""
        return self.min_or_null()

    def max_by_or_null(self, selector: Callable[[T], Any]) -> Optional[T]:
        """Returns the element with the largest value of the selector function."""
        if self.is_empty():
            return None
        return max(self._elements, key=selector)

    def max_by_or_none(self, selector: Callable[[T], Any]) -> Optional[T]:
        """Pythonic alias for max_by_or_null()."""
        return self.max_by_or_null(selector)

    def min_by_or_null(self, selector: Callable[[T], Any]) -> Optional[T]:
        """Returns the element with the smallest value of the selector function."""
        if self.is_empty():
            return None
        return min(self._elements, key=selector)

    def min_by_or_none(self, selector: Callable[[T], Any]) -> Optional[T]:
        """Pythonic alias for min_by_or_null()."""
        return self.min_by_or_null(selector)

    # Collection operations

    def fold(self, initial: R, operation: Callable[[R, T], R]) -> R:
        """Accumulates value starting with initial value and applying operation."""
        return reduce(operation, self._elements, initial)

    def reduce(self, operation: Callable[[T, T], T]) -> T:
        """Accumulates value starting with the first element."""
        if self.is_empty():
            raise ValueError("Set is empty")
        return reduce(operation, self._elements)

    def reduce_or_null(self, operation: Callable[[T, T], T]) -> Optional[T]:
        """Accumulates value starting with the first element, or returns null."""
        if self.is_empty():
            return None
        return reduce(operation, self._elements)

    def reduce_or_none(self, operation: Callable[[T, T], T]) -> Optional[T]:
        """Pythonic alias for reduce_or_null()."""
        return self.reduce_or_null(operation)

    def group_by(self, key_selector: Callable[[T], R]) -> 'KotMap[R, KotSet[T]]':
        """Groups elements by the key returned by the given key_selector function."""
        from kotcollections.kot_map import KotMap
        groups = defaultdict(list)
        for element in self._elements:
            key = key_selector(element)
            groups[key].append(element)
        return KotMap({key: KotSet(elements) for key, elements in groups.items()})

    def group_by_to(
        self,
        key_selector: Callable[[T], R],
        value_transform: Callable[[T], Any]
    ) -> 'KotMap[R, KotList[Any]]':
        """Groups values returned by value_transform by the keys returned by key_selector."""
        from kotcollections.kot_map import KotMap
        from kotcollections.kot_list import KotList
        groups = defaultdict(list)
        for element in self._elements:
            key = key_selector(element)
            value = value_transform(element)
            groups[key].append(value)
        return KotMap({key: KotList(values) for key, values in groups.items()})

    def associate(self, transform: Callable[[T], Tuple[R, Any]]) -> 'KotMap[R, Any]':
        """Returns a Map containing key-value pairs provided by transform function."""
        from kotcollections.kot_map import KotMap
        return KotMap({key: value for key, value in (transform(element) for element in self._elements)})

    def associate_by(self, key_selector: Callable[[T], R]) -> 'KotMap[R, T]':
        """Returns a Map with keys generated by key_selector and values from elements."""
        from kotcollections.kot_map import KotMap
        return KotMap({key_selector(element): element for element in self._elements})

    def associate_with(self, value_selector: Callable[[T], R]) -> 'KotMap[T, R]':
        """Returns a Map where keys are elements and values are produced by value_selector."""
        from kotcollections.kot_map import KotMap
        return KotMap({element: value_selector(element) for element in self._elements})

    # Additional convenience operations

    def find(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Returns the first element matching the given predicate, or null if not found.
        
        This is an alias for first_or_null_predicate() for Kotlin compatibility.
        """
        return self.first_or_null_predicate(predicate)

    def partition(self, predicate: Callable[[T], bool]) -> Tuple['KotSet[T]', 'KotSet[T]']:
        """Splits the original set into pair of sets.
        
        The first set contains elements for which predicate yielded true,
        while the second set contains elements for which predicate yielded false.
        """
        true_elements = []
        false_elements = []
        for element in self._elements:
            if predicate(element):
                true_elements.append(element)
            else:
                false_elements.append(element)
        return KotSet(true_elements), KotSet(false_elements)

    def for_each(self, action: Callable[[T], None]) -> None:
        """Performs the given action on each element."""
        for element in self._elements:
            action(element)

    def for_each_indexed(self, action: Callable[[int, T], None]) -> None:
        """Performs the given action on each element, providing sequential index with the element."""
        for index, element in enumerate(self._elements):
            action(index, element)

    def with_index(self) -> Iterator[Tuple[int, T]]:
        """Returns an Iterator of IndexedValue for each element of the original set."""
        return enumerate(self._elements)

    def zip(self, other: Set[R] | List[R] | 'KotSet[R]' | 'KotList[R]' | 'KotMutableList[R]') -> 'KotSet[Tuple[T, R]]':
        """Returns a set of pairs built from the elements of this set and other collection with the same index."""
        if isinstance(other, KotSet):
            other = list(other._elements)
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = list(other)
        elif isinstance(other, set):
            other = list(other)
        return KotSet(zip(self._elements, other))

    def as_sequence(self) -> Iterator[T]:
        """Creates a sequence instance that wraps the original set, allowing lazy evaluation."""
        return iter(self._elements)

    # Set operations

    def union(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> 'KotSet[T]':
        """Returns a set containing all distinct elements from both collections."""
        if isinstance(other, KotSet):
            other = other._elements
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = set(other)
        return KotSet(self._elements.union(other))

    def intersect(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> 'KotSet[T]':
        """Returns a set containing all elements that are contained by both collections."""
        if isinstance(other, KotSet):
            other = other._elements
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = set(other)
        return KotSet(self._elements.intersection(other))

    def subtract(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> 'KotSet[T]':
        """Returns a set containing all elements that are not contained in the specified collection."""
        if isinstance(other, KotSet):
            other = other._elements
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = set(other)
        return KotSet(self._elements.difference(other))

    # Operator-style set operations

    def plus(self, element: T) -> 'KotSet[T]':
        """Returns a set containing all elements of the original set and the given element."""
        result = self._elements.copy()
        result.add(element)
        return KotSet(result)

    def plus_collection(
        self,
        elements: Set[T] | List[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]'
    ) -> 'KotSet[T]':
        """Returns a set containing all elements of the original set and the given collection."""
        return self.union(elements)

    def minus(self, element: T) -> 'KotSet[T]':
        """Returns a set containing all elements of the original set except the given element."""
        result = self._elements.copy()
        result.discard(element)
        return KotSet(result)

    def minus_collection(
        self,
        elements: Set[T] | List[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]'
    ) -> 'KotSet[T]':
        """Returns a set containing all elements of the original set except those in the given collection."""
        return self.subtract(elements)

    # Conversion operations

    def to_list(self) -> List[T]:
        """Returns a Python list containing all elements."""
        return list(self._elements.copy())

    def to_set(self) -> Set[T]:
        """Returns a Python set containing all elements."""
        return set(self._elements.copy())

    def to_kot_list(self) -> 'KotList[T]':
        """Returns a Python list containing all elements."""
        from kotcollections.kot_list import KotList
        # Preserve type information when converting
        if self._element_type is not None:
            return KotList.of_type(self._element_type, list(self._elements))
        else:
            return KotList(self._elements.copy())

    def to_kot_mutable_list(self) -> 'KotMutableList[T]':
        """Returns a Python list containing all elements."""
        from kotcollections.kot_mutable_list import KotMutableList
        # Preserve type information when converting
        if self._element_type is not None:
            return KotMutableList.of_type(self._element_type, list(self._elements))
        else:
            return KotMutableList(self._elements.copy())

    def to_kot_set(self) -> KotSet[T]:
        """Returns a Python set containing all elements."""
        # Preserve type information when converting
        if self._element_type is not None:
            return KotSet.of_type(self._element_type, self._elements.copy())
        else:
            return KotSet(self._elements.copy())

    def to_kot_mutable_set(self) -> 'KotMutableSet[T]':
        """Returns a KotMutableSet containing all elements."""
        from kotcollections.kot_mutable_set import KotMutableSet
        # Preserve type information when converting
        if self._element_type is not None:
            mutable_set = KotMutableSet.of_type(self._element_type, self._elements.copy())
        else:
            mutable_set = KotMutableSet(self._elements.copy())
        return mutable_set

    def to_sorted_set(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> KotSet[T]:
        """Returns a sorted list of all elements."""
        return KotSet(sorted(self._elements, key=key, reverse=reverse))

    def join_to_string(
        self,
        separator: str = ", ",
        prefix: str = "",
        postfix: str = "",
        limit: int = -1,
        truncated: str = "...",
        transform: Optional[Callable[[T], str]] = None
    ) -> str:
        """Creates a string from all the elements separated using separator."""
        elements = list(self._elements)
        if 0 <= limit < len(elements):
            elements = elements[:limit]
            truncated_part = truncated
        else:
            truncated_part = ""

        if transform:
            elements_str = [transform(e) for e in elements]
        else:
            elements_str = [str(e) for e in elements]

        return prefix + separator.join(elements_str) + truncated_part + postfix

    # Python special methods

    def __repr__(self) -> str:
        """Return string representation of the set."""
        return f"KotSet({list(self._elements)})"

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the elements."""
        return iter(self._elements)

    def __contains__(self, item: T) -> bool:
        """Check if item is in the set."""
        return item in self._elements

    def __len__(self) -> int:
        """Return the size of the set."""
        return len(self._elements)

    def __eq__(self, other: object) -> bool:
        """Check if two sets are equal."""
        if not isinstance(other, KotSet):
            return False
        return self._elements == other._elements

    def __hash__(self) -> int:
        """Return hash of the set."""
        return hash(frozenset(self._elements))
