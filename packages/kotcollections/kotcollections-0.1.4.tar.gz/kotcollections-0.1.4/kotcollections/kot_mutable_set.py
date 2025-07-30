"""
KotMutableSet: A Python implementation of Kotlin's MutableSet interface with snake_case naming convention.
"""

from __future__ import annotations

from typing import TypeVar, Set, List, Iterator, Optional, Callable, Type, TYPE_CHECKING, Dict, Tuple

from kotcollections.kot_set import KotSet

if TYPE_CHECKING:
    from kotcollections.kot_list import KotList
    from kotcollections.kot_mutable_list import KotMutableList

T = TypeVar('T')



class KotMutableSet(KotSet[T]):
    """A Python implementation of Kotlin's MutableSet interface.
    
    This class extends KotSet with mutation methods, providing full
    Kotlin MutableSet functionality with snake_case naming.
    """

    def __init__(self, elements: Optional[Set[T] | List[T] | Iterator[T]] = None):
        """Initialize a KotMutableSet with optional elements.
        
        Args:
            elements: Initial elements for the set (set, list, or iterator)
        """
        super().__init__(elements)

    @classmethod
    def __class_getitem__(cls, element_type: Type[T]) -> Type['KotMutableSet[T]']:
        """Enable KotMutableSet[Type]() syntax for type specification.
        
        Example:
            animals = KotMutableSet[Animal]()
            animals.add(Dog("Buddy"))
            animals.add(Cat("Whiskers"))
        """
        class TypedKotMutableSet(cls):
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
        TypedKotMutableSet.__name__ = f"{cls.__name__}[{element_type.__name__}]"
        TypedKotMutableSet.__qualname__ = f"{cls.__qualname__}[{element_type.__name__}]"
        
        return TypedKotMutableSet

    @classmethod
    def of_type(cls, element_type: Type[T], elements: Optional[Set[T] | List[T] | Iterator[T]] = None) -> 'KotMutableSet[T]':
        """Create a KotMutableSet with a specific element type.
        
        This is useful when you want to create a mutable set of a parent type
        but only have instances of child types.
        
        Args:
            element_type: The type of elements this set will contain
            elements: Optional initial elements
            
        Returns:
            A new KotMutableSet instance with the specified element type
            
        Example:
            animals = KotMutableSet.of_type(Animal, [Dog("Buddy"), Cat("Whiskers")])
            # or empty set
            animals = KotMutableSet.of_type(Animal)
            animals.add(Dog("Max"))
        """
        # Use __class_getitem__ to create the same dynamic subclass
        typed_class = cls[element_type]
        return typed_class(elements)

    # Mutation operations

    def add(self, element: T) -> bool:
        """Adds the specified element to the set.
        
        Returns:
            true if the element has been added, false if the element is already in this set.
        """
        if element in self._elements:
            return False
        self._add_with_type_check(element)
        return True

    def add_all(self, elements: Set[T] | List[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> bool:
        """Adds all of the elements in the specified collection to this set.
        
        Returns:
            true if any of the specified elements was added to the set.
        """
        if isinstance(elements, KotSet):
            elements = elements._elements
        elif hasattr(elements, '_elements') and hasattr(elements, 'to_list'):
            # It's a KotList or KotMutableList
            elements = set(elements)
        elif isinstance(elements, list):
            elements = set(elements)

        initial_size = self.size
        for element in elements:
            if element not in self._elements:
                self._add_with_type_check(element)
        return self.size > initial_size

    def remove(self, element: T) -> bool:
        """Removes a single instance of the specified element from this set.
        
        Returns:
            true if the element has been successfully removed.
        """
        if element in self._elements:
            self._elements.remove(element)
            if self.is_empty():
                self._element_type = None
            return True
        return False

    def remove_all(self, elements: Set[T] | List[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> bool:
        """Removes all of this set's elements that are also contained in the specified collection.
        
        Returns:
            true if any of the specified elements was removed from the set.
        """
        if isinstance(elements, KotSet):
            elements = elements._elements
        elif hasattr(elements, '_elements') and hasattr(elements, 'to_list'):
            # It's a KotList or KotMutableList
            elements = set(elements)
        elif isinstance(elements, list):
            elements = set(elements)

        initial_size = self.size
        self._elements.difference_update(elements)
        if self.is_empty():
            self._element_type = None
        return self.size < initial_size

    def retain_all(self, elements: Set[T] | List[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> bool:
        """Retains only the elements in this set that are contained in the specified collection.
        
        Returns:
            true if any element was removed from the set.
        """
        if isinstance(elements, KotSet):
            elements = elements._elements
        elif hasattr(elements, '_elements') and hasattr(elements, 'to_list'):
            # It's a KotList or KotMutableList
            elements = set(elements)
        elif isinstance(elements, list):
            elements = set(elements)

        initial_size = self.size
        self._elements.intersection_update(elements)
        if self.is_empty():
            self._element_type = None
        return self.size < initial_size

    def clear(self) -> None:
        """Removes all elements from this set."""
        self._elements.clear()
        self._element_type = None

    # Additional mutation operations

    def remove_if(self, predicate: Callable[[T], bool]) -> bool:
        """Removes all elements that match the given predicate.
        
        Returns:
            true if any elements were removed.
        """
        to_remove = [element for element in self._elements if predicate(element)]
        if to_remove:
            for element in to_remove:
                self._elements.remove(element)
            if self.is_empty():
                self._element_type = None
            return True
        return False

    def retain_if(self, predicate: Callable[[T], bool]) -> bool:
        """Retains only elements that match the given predicate.
        
        Returns:
            true if any elements were removed.
        """
        to_remove = [element for element in self._elements if not predicate(element)]
        if to_remove:
            for element in to_remove:
                self._elements.remove(element)
            if self.is_empty():
                self._element_type = None
            return True
        return False

    # Union/Intersection/Difference with mutation

    def union_update(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> None:
        """Adds all elements from the other collection to this set."""
        if isinstance(other, KotSet):
            other = other._elements
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = set(other)
        for element in other:
            if element not in self._elements:
                self._add_with_type_check(element)

    def intersect_update(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> None:
        """Retains only elements that are contained in the specified collection."""
        if isinstance(other, KotSet):
            other = other._elements
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = set(other)
        self._elements.intersection_update(other)
        if self.is_empty():
            self._element_type = None

    def subtract_update(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> None:
        """Removes all elements that are contained in the specified collection."""
        if isinstance(other, KotSet):
            other = other._elements
        elif hasattr(other, '_elements') and hasattr(other, 'to_list'):
            # It's a KotList or KotMutableList
            other = set(other)
        self._elements.difference_update(other)
        if self.is_empty():
            self._element_type = None

    # Operator overloads for mutation

    def __iadd__(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> 'KotMutableSet[T]':
        """In-place union using += operator."""
        self.union_update(other)
        return self

    def __isub__(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> 'KotMutableSet[T]':
        """In-place subtraction using -= operator."""
        self.subtract_update(other)
        return self

    def __iand__(self, other: Set[T] | 'KotSet[T]' | 'KotList[T]' | 'KotMutableList[T]') -> 'KotMutableSet[T]':
        """In-place intersection using &= operator."""
        self.intersect_update(other)
        return self

    def __repr__(self) -> str:
        """Return string representation of the mutable set."""
        return f"KotMutableSet({list(self._elements)})"
