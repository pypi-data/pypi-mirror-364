from __future__ import annotations

import random
from functools import cmp_to_key
from typing import TypeVar, Optional, Callable, Iterable, List, Type

from kotcollections.kot_list import KotList

T = TypeVar('T')


class KotMutableList(KotList[T]):
    def __init__(self, elements: Optional[Iterable[T]] = None):
        super().__init__(elements)

    @classmethod
    def __class_getitem__(cls, element_type: Type[T]) -> Type['KotMutableList[T]']:
        """Enable KotMutableList[Type]() syntax for type specification.
        
        Example:
            animals = KotMutableList[Animal]()
            animals.add(Dog("Buddy"))
            animals.add(Cat("Whiskers"))
        """
        class TypedKotMutableList(cls):
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
        TypedKotMutableList.__name__ = f"{cls.__name__}[{element_type.__name__}]"
        TypedKotMutableList.__qualname__ = f"{cls.__qualname__}[{element_type.__name__}]"
        
        return TypedKotMutableList

    @classmethod
    def of_type(cls, element_type: Type[T], elements: Optional[Iterable[T]] = None) -> 'KotMutableList[T]':
        """Create a KotMutableList with a specific element type.
        
        This is useful when you want to create a mutable list of a parent type
        but only have instances of child types.
        
        Args:
            element_type: The type of elements this list will contain
            elements: Optional initial elements
            
        Returns:
            A new KotMutableList instance with the specified element type
            
        Example:
            animals = KotMutableList.of_type(Animal, [Dog("Buddy"), Cat("Whiskers")])
            # or empty list
            animals = KotMutableList.of_type(Animal)
            animals.add(Dog("Max"))
        """
        # Use __class_getitem__ to create the same dynamic subclass
        typed_class = cls[element_type]
        return typed_class(elements)

    def __setitem__(self, index: int, value: T) -> None:
        self.set(index, value)

    def __delitem__(self, index: int) -> None:
        self.remove_at(index)

    def add(self, element: T) -> bool:
        self._check_type(element)
        self._elements.append(element)
        return True

    def add_at(self, index: int, element: T) -> None:
        if not 0 <= index <= self.size:
            raise IndexError(f"Index {index} out of bounds for insertion")
        self._check_type(element)
        self._elements.insert(index, element)

    def add_all(self, elements: Iterable[T]) -> bool:
        elements_list = list(elements)
        if elements_list:
            for element in elements_list:
                self._check_type(element)
            self._elements.extend(elements_list)
            return True
        return False

    def add_all_at(self, index: int, elements: Iterable[T]) -> bool:
        if not 0 <= index <= self.size:
            raise IndexError(f"Index {index} out of bounds for insertion")
        elements_list = list(elements)
        if elements_list:
            for element in elements_list:
                self._check_type(element)
            for i, element in enumerate(elements_list):
                self._elements.insert(index + i, element)
            return True
        return False

    def set(self, index: int, element: T) -> T:
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of bounds for list of size {self.size}")
        self._check_type(element)
        old_element = self._elements[index]
        self._elements[index] = element
        return old_element

    def remove_at(self, index: int) -> T:
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of bounds for list of size {self.size}")
        return self._elements.pop(index)

    def remove(self, element: T) -> bool:
        try:
            self._elements.remove(element)
            return True
        except ValueError:
            return False

    def remove_all(self, elements: Iterable[T]) -> bool:
        elements_set = set(elements)
        initial_size = self.size
        self._elements = [e for e in self._elements if e not in elements_set]
        return self.size < initial_size

    def remove_first(self) -> T:
        """Removes the first element from this mutable list."""
        if self.is_empty():
            raise IndexError("List is empty")
        return self._elements.pop(0)

    def remove_last(self) -> T:
        """Removes the last element from this mutable list."""
        if self.is_empty():
            raise IndexError("List is empty")
        return self._elements.pop()

    def remove_first_or_null(self) -> Optional[T]:
        """Removes the first element from this mutable list and returns it, or null if the list is empty."""
        if self.is_empty():
            return None
        return self._elements.pop(0)

    def remove_first_or_none(self) -> Optional[T]:
        """Alias for remove_first_or_null() - more Pythonic naming."""
        return self.remove_first_or_null()

    def remove_last_or_null(self) -> Optional[T]:
        """Removes the last element from this mutable list and returns it, or null if the list is empty."""
        if self.is_empty():
            return None
        return self._elements.pop()

    def remove_last_or_none(self) -> Optional[T]:
        """Alias for remove_last_or_null() - more Pythonic naming."""
        return self.remove_last_or_null()

    def retain_all(self, elements: Iterable[T]) -> bool:
        elements_set = set(elements)
        initial_size = self.size
        self._elements = [e for e in self._elements if e in elements_set]
        return self.size < initial_size

    def clear(self) -> None:
        self._elements.clear()

    def sort(self, key: Optional[Callable[[T], any]] = None, reverse: bool = False) -> None:
        self._elements.sort(key=key, reverse=reverse)

    def sort_descending(self) -> None:
        self._elements.sort(reverse=True)

    def sort_by(self, selector: Callable[[T], any]) -> None:
        self._elements.sort(key=selector)

    def sort_by_descending(self, selector: Callable[[T], any]) -> None:
        self._elements.sort(key=selector, reverse=True)

    def sort_with(self, comparator: Callable[[T, T], int]) -> None:
        """Sorts elements in the list in-place according to the specified comparator."""
        self._elements.sort(key=cmp_to_key(comparator))

    def reverse(self) -> None:
        self._elements.reverse()

    def shuffle(self, random_instance: Optional[random.Random] = None) -> None:
        if random_instance:
            random_instance.shuffle(self._elements)
        else:
            random.shuffle(self._elements)

    def fill(self, value: T) -> None:
        for i in range(self.size):
            self._elements[i] = value

    def as_reversed(self) -> 'KotMutableList[T]':
        class KotReversedMutableList(KotMutableList[T]):
            def __init__(self, original: KotMutableList[T]):
                self._original = original
                super().__init__()

            @property
            def _elements(self) -> List[T]:
                return list(reversed(self._original._elements))

            @_elements.setter
            def _elements(self, value: List[T]) -> None:
                pass

            def __getitem__(self, index: int) -> T:
                return self._original._elements[self._original.size - 1 - index]

            def __setitem__(self, index: int, value: T) -> None:
                self._original._elements[self._original.size - 1 - index] = value

            def __len__(self) -> int:
                return self._original.size

        return KotReversedMutableList(self)
