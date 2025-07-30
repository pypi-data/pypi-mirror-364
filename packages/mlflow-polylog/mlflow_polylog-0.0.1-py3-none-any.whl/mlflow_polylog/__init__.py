"""Top-level module for the mlflow_polylog package.

This module exposes the main imperative logging interface for the polymodel library,
including functions for logging models and registering custom log handlers.
"""

from mlflow_polylog.defaults import get_default_log
from mlflow_polylog.functions import log_model, register_log
from mlflow_polylog.log import PolymorphicModelLog
from mlflow_polylog.type_mapping import TypeMapping
