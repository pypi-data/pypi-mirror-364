# AutoML Class API Reference

## Overview
The `AutoML` class serves as the primary interface for automated machine learning, providing a high-level API for model training, evaluation, and prediction.

## Class Signature
```python
class AutoML:
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    )
```

## Constructor Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `config` | `Dict[str, Any]` | Configuration dictionary | `None` |

### Configuration Options
- `problem_type`: 'classification' or 'regression'
- `random_state`: Random seed for reproducibility
- `custom_models`: Dictionary of custom models to register

## Key Methods

### `fit(X, y)`
Train models on the provided data.

**Parameters:**
- `X`: Feature matrix
- `y`: Target variable

**Returns:** `self`

**Example:**
```python
automl.fit(X_train, y_train)
```

### `evaluate(X, y)`
Evaluate models on test data, detecting overfitting.

**Parameters:**
- `X`: Test feature matrix
- `y`: Test target variable

**Returns:** `Dict` containing evaluation results

**Example:**
```python
results = automl.evaluate(X_test, y_test)
```

### `predict(X)`
Make predictions using the best model.

**Parameters:**
- `X`: Feature matrix for prediction

**Returns:** Predicted labels/values

**Example:**
```python
predictions = automl.predict(X_test)
```

### `predict_proba(X)`
Get prediction probabilities (classification only).

**Parameters:**
- `X`: Feature matrix for prediction

**Returns:** Prediction probabilities

**Example:**
```python
probabilities = automl.predict_proba(X_test)
```

## Advanced Methods

### `register_model(name, model_instance, preprocessor=None)`
Register a custom model with the framework.

**Parameters:**
- `name`: Model identifier
- `model_instance`: Scikit-learn compatible model
- `preprocessor`: Optional custom preprocessor

**Example:**
```python
from sklearn.ensemble import ExtraTreesClassifier

automl.register_model(
    'ExtraTrees',
    ExtraTreesClassifier(n_estimators=200)
)
```

### `get_leaderboard()`
Retrieve a performance comparison of trained models.

**Returns:** `DataFrame` with model performance metrics

**Example:**
```python
leaderboard = automl.get_leaderboard()
print(leaderboard)
```

### `get_feature_importance(model_name=None)`
Analyze feature contributions to predictions.

**Parameters:**
- `model_name`: Optional specific model name

**Returns:** Feature importance dictionary

**Example:**
```python
importance = automl.get_feature_importance()
```

### `get_improvement_suggestions(model_name=None)`
Receive recommendations for model improvement.

**Parameters:**
- `model_name`: Optional specific model name

**Returns:** List of improvement suggestions

**Example:**
```python
suggestions = automl.get_improvement_suggestions()
```

## Overfitting Control

### `pipeline.set_overfitting_control()`
Configure overfitting detection and mitigation.

**Parameters:**
- `detection_enabled`: Enable overfitting detection
- `auto_mitigation`: Automatically mitigate overfitting
- `threshold`: Sensitivity level

**Example:**
```python
automl.pipeline.set_overfitting_control(
    detection_enabled=True,
    auto_mitigation=True,
    threshold=0.3
)
```

## Model Persistence

### `save_best_model(path)`
Save the best-performing model.

**Parameters:**
- `path`: File path to save the model

**Example:**
```python
automl.save_best_model('best_model.pkl')
```

### `load_model(path)`
Load a previously saved model.

**Parameters:**
- `path`: File path of the saved model

**Returns:** Loaded model

**Example:**
```python
loaded_model = automl.load_model('best_model.pkl')
```

## Error Handling
- Raises `ValueError` for incompatible data
- Provides informative error messages
- Logs diagnostic information

## Compatibility
- Works with scikit-learn compatible models
- Supports numpy arrays and pandas DataFrames
- Handles classification and regression problems

## Example Workflow
```python
from automl import AutoML
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load and prepare data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create and use AutoML
automl = AutoML(problem_type='classification')
automl.fit(X_train, y_train)
results = automl.evaluate(X_test, y_test)
predictions = automl.predict(X_test)
```

---

<div align="center">
🚀 **Simplifying Machine Learning Automation** 🤖
</div>
