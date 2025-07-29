# Model Wrapper API Reference

## Overview
The Model Wrapper provides a standardized interface for machine learning models, adding advanced tracking, preprocessing, and management capabilities.

## Class Signature
```python
class ModelWrapper:
    def __init__(
        self,
        name: str,
        model_instance: BaseEstimator,
        preprocessor: Optional[Preprocessor] = None
    )
```

## Constructor Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `name` | `str` | Unique model identifier | Required |
| `model_instance` | `BaseEstimator` | Scikit-learn compatible model | Required |
| `preprocessor` | `Optional[Preprocessor]` | Data preprocessor | `StandardPreprocessor()` |

## Key Methods

### `fit(X, y)`
Train the model with optional preprocessing.

**Parameters:**
- `X`: Feature matrix
- `y`: Target variable

**Returns:** `self`

**Example:**
```python
wrapper.fit(X_train, y_train)
```

### `predict(X)`
Make predictions using the wrapped model.

**Parameters:**
- `X`: Feature matrix for prediction

**Returns:** Predicted labels/values

**Example:**
```python
predictions = wrapper.predict(X_test)
```

### `predict_proba(X)`
Get prediction probabilities (for classification).

**Parameters:**
- `X`: Feature matrix for prediction

**Returns:** Prediction probabilities

**Example:**
```python
probabilities = wrapper.predict_proba(X_test)
```

## Advanced Methods

### `get_training_log()`
Retrieve detailed training information.

**Returns:** `Dict` with training metadata

**Example:**
```python
log = wrapper.get_training_log()
print("Training Duration:", log['training_duration'])
```

### `get_feature_importance()`
Analyze feature contributions to predictions.

**Returns:** `Dict` or `None` with feature importance

**Example:**
```python
importance = wrapper.get_feature_importance()
```

### `save(path)`
Save the model to disk.

**Parameters:**
- `path`: File path to save the model

**Example:**
```python
wrapper.save('model_path.pkl')
```

### `load(path)` (Class Method)
Load a previously saved model.

**Parameters:**
- `path`: File path of the saved model

**Returns:** Loaded `ModelWrapper` instance

**Example:**
```python
loaded_model = ModelWrapper.load('model_path.pkl')
```

## Training Log Details

The training log includes:
- Start and end times
- Training duration
- Number of samples and features
- Model parameters
- Preprocessor information
- Memory usage
- Warnings and errors

**Example Log Structure:**
```python
{
    'start_time': '2024-02-15 10:30:45',
    'end_time': '2024-02-15 10:31:12',
    'training_duration': 27.5,
    'n_samples': 150,
    'n_features': 4,
    'model_params': {...},
    'preprocessor_info': 'StandardPreprocessor',
    'memory_usage': {
        'current_mb': 50.5,
        'peak_mb': 75.2
    },
    'warnings': [...]
}
```

## Error Handling
- Comprehensive logging of training errors
- Detailed diagnostic information
- Graceful error management

## Preprocessing Integration
- Automatic data transformation
- Supports custom preprocessors
- Handles different data types

## Example Workflow
```python
from automl import ModelWrapper
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris

# Load data
X, y = load_iris(return_X_y=True)

# Create model wrapper
wrapper = ModelWrapper(
    name='IrisRandomForest',
    model_instance=RandomForestClassifier(),
    preprocessor=StandardScaler()
)

# Full model lifecycle
wrapper.fit(X, y)
training_log = wrapper.get_training_log()
predictions = wrapper.predict(X)
feature_importance = wrapper.get_feature_importance()

# Save and load
wrapper.save('iris_model.pkl')
loaded_model = ModelWrapper.load('iris_model.pkl')
```

## Compatibility
- Works with scikit-learn compatible models
- Supports various preprocessors
- Handles both classification and regression

## Performance Considerations
- Minimal overhead
- Efficient logging
- Memory-conscious design

## Visualization Support
- Training progress tracking
- Feature importance analysis
- Performance monitoring

---

<div align="center">
🚀 **Standardizing Machine Learning Model Management** 🤖
</div>
