# mlflow-polylog

A polymorphic model logging utility for MLflow that enables seamless logging of machine learning models from various libraries without requiring explicit type specification or installation of all supported frameworks. It dynamically detects installed libraries and maps model types to the appropriate MLflow logging functions.

## Features

- Automatic detection of installed ML libraries (e.g., scikit-learn, XGBoost, LightGBM, etc.).
- Type-agnostic model logging via a unified interface.
- Extensible architecture for registering custom logging handlers.
- Built-in support for popular frameworks like CatBoost, PyTorch, TensorFlow, and more.
- Lazy initialization to minimize overhead.

## Installation

Install the package using pip:

```
pip install mlflow-polylog
```

This package requires Python >= 3.10 and MLflow >= 2.13.0. Optional dependencies for testing include pytest and various ML libraries (e.g., catboost, lightgbm, xgboost, scikit-learn).

For development, install optional extras:

- Testing: `pip install mlflow-polylog[tests]`
- Linting: `pip install mlflow-polylog[lint]`
- Typing: `pip install mlflow-polylog[typing]`

## Quick Start

Import the main functions and start logging models within an MLflow run:

```python
import mlflow
from mlflow_polylog import log_model

with mlflow.start_run():
    # Assume 'model' is your trained model (e.g., from scikit-learn)
    log_model(model, artifact_path="model")
```

## Usage Examples

### Using `log_model`

The `log_model` function provides an imperative interface to log models similar to MLflow's native methods. It automatically selects the appropriate logging handler based on the model's type.

```python
import mlflow
from sklearn.linear_model import LogisticRegression
from mlflow_polylog import log_model

# Train a simple model
model = LogisticRegression()
# Assume X_train, y_train are defined
model.fit(X_train, y_train)

with mlflow.start_run():
    log_model(
        model,
        artifact_path="sklearn_model",
        input_example=X_train[:5]  # Optional: for model signature inference
    )
```

This logs the scikit-learn model to MLflow without needing to import or call `mlflow.sklearn.log_model` explicitly.

### Using `register_log`

Register a custom logging function for a specific model type to extend the default behavior.

```python
import mlflow
from typing import Any
from mlflow_polylog import register_log, log_model

# Define a custom log function
def custom_log_func(model: Any, artifact_path: str, **kwargs):
    # Custom logging logic, e.g., wrapping in pyfunc
    mlflow.pyfunc.log_model(artifact_path=artifact_path, python_model=model, **kwargs)

# Register it for a custom model type
class CustomModel:
    pass

register_log(CustomModel, custom_log_func)

# Now log an instance
custom_model = CustomModel()

with mlflow.start_run():
    log_model(custom_model, artifact_path="custom_model")
```

This adds support for `CustomModel` and uses the custom function when logging.

### Using `PolymorphicModelLog`

For more advanced usage, instantiate `PolymorphicModelLog` directly to manage logging mappings. This is useful in production environments where you need fine-grained control.

```python
import mlflow
from mlflow_polylog import PolymorphicModelLog, get_default_log
from mlflow_polylog.type_mapping import TypeMapping

# Get the default log mapper
default_log = get_default_log()

# Create a custom mapping (example: add a wrapper for a specific type)
custom_mapping = TypeMapping({str: lambda m, **kw: print(f"Logging string model: {m}")})

# Initialize PolymorphicModelLog with combined mappings
poly_log = PolymorphicModelLog(TypeMapping(default_log._log_map, custom_mapping))

# Use it to log
with mlflow.start_run():
    poly_log(model, artifact_path="model")  # 'model' is your trained model
```

You can also chain additions using `add_log`:

```python
poly_log = get_default_log().add_log(CustomType, custom_log_func)
poly_log(model_of_custom_type, artifact_path="model")
```

## Supported Libraries

The package automatically supports logging for models from the following libraries if they are installed:

- CatBoost
- LightGBM
- XGBoost
- scikit-learn
- PyTorch
- TensorFlow
- fastai
- MXNet (Gluon)
- StatsModels
- Prophet
- PaddlePaddle
- spaCy
- H2O
- MLflow PyFunc (including callables)

Add more via `register_log` as needed.

## Testing

Run tests with pytest:

```
python -m pytest tests
```

Some tests are marked as slow and require optional ML library installations.
