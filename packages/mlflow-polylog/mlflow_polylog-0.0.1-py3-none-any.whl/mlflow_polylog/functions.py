"""Provide an imperative MLflow-like interface for the polymodel library.

This module offers convenient functions for logging models in a style similar to MLflow.
It is intended for use in simple scripts or Jupyter notebooks and is not recommended for
production environments.

Main functionality includes:
    - Logging models with customizable handlers.
    - Registering custom log functions for different model types.
"""

from typing import Any

from mlflow_polylog._internal import GLOBAL_LOG_STORE
from mlflow_polylog.log import LogModelFunctionType


def log_model(model: Any, *args: Any, **kwargs: dict[str, Any]) -> None:
    """Log a model using the currently registered log function.

    Logs the provided model using the log function registered for its type. Additional
    arguments and keyword arguments are passed to the log handler.

    Args:
        model : The model instance to log. Type and requirements depend on the
            registered log handler.
        *args : Additional positional arguments to pass to the log handler.
        **kwargs : Additional keyword arguments to pass to the log handler.

    Returns:
        None. The function performs logging as a side effect.

    Raises:
        Exception : If no suitable log handler is registered for the model type.
    """
    log = GLOBAL_LOG_STORE.get()
    log(model, *args, **kwargs)


def register_log(model_type: type[Any], log_model_function: LogModelFunctionType) -> None:
    """Register a custom log function for a given model type.

    Associates a log handler with the specified model type. The handler will be used
    when logging models of this type via `log_model`.

    Args:
        model_type : The type of model for which the log handler is being registered.
        log_model_function : A callable that implements the logging logic for the
            specified model type. Must accept the model instance as its first argument.

    Returns:
        None. The function updates the global log handler registry.

    Raises:
        Exception : If the registration process fails due to invalid arguments or
            internal errors.
    """
    log = GLOBAL_LOG_STORE.get()
    log = log.add_log(model_type, log_model_function)
    GLOBAL_LOG_STORE.update(log)
