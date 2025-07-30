"""Provide a type-based mapping utility for Python types."""

from collections.abc import Iterator, Mapping, Sequence
from types import GenericAlias
from typing import Any, TypeVar, get_origin

ValueType = TypeVar('ValueType')


class AmbiguousTypeError(RuntimeError):
    """Signal an ambiguous match while resolving a type look-up.

    The exception is raised when more than one stored type key matches the
    instance supplied to `TypeMapping.__getitem__`.  It captures the
    value that triggered the ambiguity as well as all candidate type keys so
    that callers can decide how to disambiguate.
    """

    def __init__(
        self,
        message: str,
        value_to_find: Any,
        finded_keys: Sequence[type],
    ) -> None:
        """Initialise the exception with context information.

        Args:
            message: Human-readable explanation of the failure.
            value_to_find: The instance (not the type) that could not be resolved
                unambiguously.
            finded_keys: Sequence of type keys that matched the given instance.
        """
        super().__init__(message)
        self.value_to_find = value_to_find
        self.finded_keys = finded_keys

    def __str__(self) -> str:
        """Return the official string representation of the exception."""
        return (
            self.__class__.__name__
            + f'(message={self.args[0]},'
            + f' value={self.value_to_find},'
            + f' types={self.finded_keys})'
        )


class TypeMapping(Mapping[type, ValueType]):
    """Implement a read-only mapping from ``type`` keys to arbitrary values.

    The mapping behaves like a lightweight *dispatcher* that returns the value
    registered for the first type key for which ``isinstance(key, type_key)``
    evaluates to ``True``.  Because subclass relationships would introduce
    ambiguity, the constructor refuses to store overlapping type keys.

    Example:
        >>> tm = TypeMapping({int: "integer", str: "string"})
        >>> tm[5]
        'integer'
        >>> tm["hello"]
        'string'
    """

    def __init__(self, *initial_mappings: Mapping[type, ValueType]) -> None:
        """Create a :class:`TypeMapping` from one or more dictionaries.

        All keys are normalised so that ``list[int]`` and similar
        :class:`types.GenericAlias` objects are replaced by their origin
        ``list``.  Keys must be real ``type`` objects and must not stand in a
        subclass relationship with any other key.

        Args:
            *initial_mappings: Arbitrary number of ``Mapping`` objects whose
                keys are Python types and whose values are of any type.

        Raises:
            TypeError: If a key is not a Python ``type`` (after origin
                normalisation) or if duplicate normalised keys are supplied.
        """
        mapping = {}
        for initial_mapping in initial_mappings:
            for key, value in initial_mapping.items():
                origin_key = get_origin(key) if isinstance(key, GenericAlias) else key

                if not isinstance(origin_key, type):
                    raise TypeError(f'Key {key} must be a type')

                mapping[origin_key] = value

        self._map = mapping

    def __getitem__(self, key: Any) -> ValueType:
        """Return the value whose type key matches *key*.

        The method iterates over the stored type keys in insertion order and
        returns the first associated value for which ``isinstance(key,
        type_key)`` holds.

        Args:
            key: The object used to determine the appropriate type key.

        Returns:
            The value associated with the matching type key.

        Raises:
            KeyError: If no stored key matches the type of *key*.
            AmbiguousTypeError: If more than one stored key matches *key*.
        """
        keys = []
        values = []
        for type_key, value in self._map.items():
            if isinstance(key, type_key):
                keys.append(type_key)
                values.append(value)

        if len(keys) == 0:
            raise KeyError(f'No type found for instance {key} of type {type(key)}')

        if len(keys) > 1:
            raise AmbiguousTypeError(
                'Too many types found',
                value_to_find=key,
                finded_keys=keys,
            )

        return values[0]

    def __iter__(self) -> Iterator[type]:
        """Return an iterator over stored type keys."""
        return iter(self._map.keys())

    def __len__(self) -> int:
        """Return the number of key value pairs stored in the mapping."""
        return len(self._map)

    def __repr__(self) -> str:
        """Return the developer-oriented string representation of the mapping."""
        return f'TypeMapping({dict(self._map)})'
