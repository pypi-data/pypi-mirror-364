"""Utility helpers for global polymorphic model log method management.

This module provides a global store for managing a single instance of a polymorphic
model log method. It ensures that logging methods for models can be accessed and
updated globally, with support for lazy initialization using a default log method.
"""

from mlflow_polylog.defaults import get_default_log
from mlflow_polylog.log import PolymorphicModelLog


class GlobalStore:
    """Store exactly one polymorphic model log method instance.

    Provides a mechanism for globally accessing and updating the current
    polymorphic model log method. This is useful for centralizing logging
    behavior across different parts of an application that use polymorphic
    model logging.
    """

    def __init__(self) -> None:
        """Create instance of GlobalStore without any arguments."""
        self._method: PolymorphicModelLog | None = None

    def get(self) -> PolymorphicModelLog:
        """Return the currently stored polymorphic model log method.

        If no method has been set, this will lazily initialize the store with the
        default mlflow log method using `mlflow_polylog.defaults.get_default_log`.
        This approach helps avoid expensive imports or initialization until the log
        method is actually needed.

        Returns:
            PolymorphicModelLog: The log method instance managed by the store.
        """
        if self._method is None:
            self._method = get_default_log()
        return self._method

    def update(self, new_method: PolymorphicModelLog) -> None:
        """Replace the stored polymorphic model log method.

        Updates the store with a new instance of a polymorphic model log method,
        replacing any previously stored instance.

        Args:
            new_method: The new log method instance that should replace the
                existing one.
        """
        self._method = new_method


GLOBAL_LOG_STORE = GlobalStore()
