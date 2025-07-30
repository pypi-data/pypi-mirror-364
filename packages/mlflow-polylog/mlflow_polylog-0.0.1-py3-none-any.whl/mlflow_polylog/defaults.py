"""This module provides default logging and loading utilities for polymorphic ML models.

The module dynamically detects installed ML libraries and maps their model types to the
appropriate MLflow log_model functions. It exposes functions to retrieve default logging
and loading handlers for use with the mlflow_polylog package.
"""

import importlib
from collections.abc import Callable
from typing import Any

import mlflow

from mlflow_polylog.log import PolymorphicModelLog, wrap_log
from mlflow_polylog.type_mapping import TypeMapping


def _is_installed(package_name: str) -> bool:
    """Determine if a package is installed in the current environment.

    Args:
        package_name : The name of the package to check for installation.

    Returns:
        True if the package is installed, False otherwise.
    """
    return importlib.util.find_spec(package_name) is not None


def get_default_log() -> PolymorphicModelLog:
    """Return a default polymorphic logging handler for supported ML model types.

    Dynamically inspects the current environment for installed ML libraries and builds a
    mapping from model types to their corresponding MLflow log_model functions. The
    returned PolymorphicModelLog instance can be used to log a variety of model types
    without requiring manual configuration.

    Returns:
        A PolymorphicModelLog instance with type mappings for all supported and installed
        model libraries.
    """
    pyfunc_wrapped_log = wrap_log('python_model', mlflow.pyfunc.log_model)
    available_logs = {
        mlflow.pyfunc.PythonModel: pyfunc_wrapped_log,
        Callable[..., Any]: pyfunc_wrapped_log,
    }

    if _is_installed('catboost'):
        import catboost

        available_logs[catboost.CatBoost] = mlflow.catboost.log_model

    if _is_installed('lightgbm'):
        import lightgbm

        available_logs[lightgbm.Booster] = mlflow.lightgbm.log_model

    if _is_installed('xgboost'):
        import xgboost

        available_logs[xgboost.Booster] = mlflow.xgboost.log_model

    if _is_installed('sklearn'):
        import sklearn.base

        available_logs[sklearn.base.BaseEstimator] = mlflow.sklearn.log_model

    if _is_installed('torch'):
        import torch.nn

        available_logs[torch.nn.Module] = mlflow.pytorch.log_model

    if _is_installed('tensorflow'):
        import tensorflow as tf

        available_logs[tf.keras.Model] = mlflow.tensorflow.log_model

    if _is_installed('fastai'):
        from fastai.learner import Learner

        available_logs[Learner] = mlflow.fastai.log_model

    if _is_installed('mxnet'):
        from mxnet.gluon import Block

        available_logs[Block] = mlflow.gluon.log_model

    if _is_installed('statsmodels'):
        import statsmodels.base.model

        available_logs[statsmodels.base.model.Model] = mlflow.statsmodels.log_model

    if _is_installed('prophet'):
        from prophet.forecaster import Prophet

        available_logs[Prophet] = mlflow.prophet.log_model

    if _is_installed('paddlepaddle'):
        import paddle

        available_logs[paddle.nn.Layer] = mlflow.paddle.log_model

    if _is_installed('spacy'):
        import spacy.language

        available_logs[spacy.language.Language] = mlflow.spacy.log_model

    if _is_installed('h2o'):
        import h2o

        available_logs[h2o.model.model_base.ModelBase] = mlflow.h2o.log_model

    return PolymorphicModelLog(TypeMapping(available_logs))
