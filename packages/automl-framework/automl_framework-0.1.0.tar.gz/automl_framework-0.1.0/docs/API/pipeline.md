# AutoML Pipeline API Reference

## Overview
The AutoML Pipeline is the core engine of the framework, managing the entire machine learning workflow from data preprocessing to model evaluation.

## Class Signature
```python
class AutoMLPipeline:
    def __init__(
        self,
        problem_type: str = 'classification',
        random_state: int = 42
    )
```

## Constructor Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `problem_type` | `str` | 'classification' or 'regression' | 'classification' |
| `random_state` | `int` | Random seed for reproducibility | 42 |

## Key Methods

### `fit(X, y)`
Train registered models on the provided data.

**Parameters:**
- `X`: Feature matrix
- `y`: Target variable

**Returns:** `self`

**Example:**
```python
pipeline.fit(X_train, y_train)
```

### `evaluate(X, y)`
Evaluate models on test data, detecting overfitting.

**Parameters:**
- `X`: Test feature matrix
- `y`: Test target variable

**Returns:** `Dict` of evaluation results

**Example:**
```python
results = pipeline.evaluate(X_test, y_test)
```

### `set_overfitting_control()`
Configure overfitting detection and mitigation strategies.

**Parameters:**
- `detection_enabled`: Enable overfitting detection
- `auto_mitigation`: Automatically mitigate overfitting
- `threshold`: Sensitivity level for mitigation

**Example:**
```python
pipeline.set_overfitting_control(
    detection_enabled=True,
    auto_mitigation=True,
    threshold=0.3
)
```

## Advanced Methods

### `register_model(name, model_instance, preprocessor=None)`
Register a custom model with the pipeline.

**Parameters:**
- `name`: Model identifier
- `model_instance`: Scikit-learn compatible model
- `preprocessor`: Optional custom preprocessor

**Example:**
```python
from sklearn.ensemble import ExtraTreesClassifier

pipeline.register_model(
    'ExtraTrees',
    ExtraTreesClassifier(n_estimators=200)
)
```

### `get_leaderboard()`
Retrieve a comprehensive performance comparison of trained models.

**Returns:** `DataFrame` with model performance metrics

**Example:**
```python
leaderboard = pipeline.get_leaderboard()
print(leaderboard)
```

### `get_best_model()`
Retrieve the best-performing model based on evaluation metrics.

**Returns:** Best model instance

**Example:**
```python
best_model = pipeline.get_best_model()
```

## Overfitting Management

### Overfitting Detection Methods
- Calculates train-test performance gaps
- Identifies overfitting severity
- Provides mitigation strategies

**Example:**
```python
# Get overfitting assessment
assessment = pipeline.get_overfitting_assessment('RandomForest')
print("Overfitting Severity:", assessment['severity'])
```

### Mitigation Strategies
- Regularization
- Feature selection
- Early stopping
- Ensemble methods

**Example:**
```python
# Get mitigation strategies
strategies = pipeline.get_mitigation_strategies('RandomForest')
for strategy in strategies:
    print(f"Strategy: {strategy['name']}")
    print(f"Description: {strategy['description']}")
```

## Model Registry Interactions

### `unregister_model(name)`
Remove a model from the pipeline.

**Parameters:**
- `name`: Model identifier to remove

**Example:**
```python
pipeline.unregister_model('UnwantedModel')
```

### `get_model_reference(model_name=None)`
Get information about registered models.

**Parameters:**
- `model_name`: Optional specific model name

**Returns:** Dictionary of model information

**Example:**
```python
model_info = pipeline.get_model_reference('RandomForest')
```

## Performance and Diagnostics

### `get_training_summary()`
Retrieve overall training process summary.

**Returns:** `Dict` with training details

**Example:**
```python
summary = pipeline.get_training_summary()
print("Total Training Time:", summary['total_duration'])
```

### `get_all_training_logs()`
Get training logs for all models.

**Returns:** Dictionary of training logs

**Example:**
```python
logs = pipeline.get_all_training_logs()
```

## Error Handling
- Comprehensive error logging
- Informative exception messages
- Detailed diagnostic information

## Compatibility
- Scikit-learn compatible models
- Supports numpy and pandas data structures
- Handles both classification and regression

## Example Workflow
```python
from automl import AutoMLPipeline
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Create pipeline
pipeline = AutoMLPipeline(problem_type='classification')

# Load and prepare data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Full machine learning workflow
pipeline.fit(X_train, y_train)
results = pipeline.evaluate(X_test, y_test)
leaderboard = pipeline.get_leaderboard()
```

---

<div align="center">
🚀 **Powering Intelligent Machine Learning Workflows** 🤖
</div>
