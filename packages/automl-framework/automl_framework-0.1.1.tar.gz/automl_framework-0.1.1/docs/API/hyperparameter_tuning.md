# Hyperparameter Tuning API Reference

## Overview
The Hyperparameter Tuner provides advanced optimization strategies for finding optimal model configurations across various machine learning algorithms.

## Class Signature
```python
class HyperparameterTuner:
    def __init__(
        self,
        problem_type: str = 'classification',
        cv: int = 5,
        random_state: int = 42,
        n_jobs: int = -1,
        verbose: int = 1
    )
```

## Constructor Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `problem_type` | `str` | 'classification' or 'regression' | 'classification' |
| `cv` | `int` | Number of cross-validation folds | 5 |
| `random_state` | `int` | Random seed for reproducibility | 42 |
| `n_jobs` | `int` | Number of parallel jobs (-1 for all CPUs) | -1 |
| `verbose` | `int` | Verbosity level | 1 |

## Key Methods

### `tune_model(model_name, model_instance, X, y)`
Perform hyperparameter tuning for a specific model.

**Parameters:**
- `model_name`: Name of the model
- `model_instance`: Model to tune
- `X`: Feature matrix
- `y`: Target variable

**Returns:** `Dict` with tuning results

**Example:**
```python
results = tuner.tune_model(
    'RandomForest',
    RandomForestClassifier(),
    X_train,
    y_train
)
```

### `tune_multiple_models(models_dict, X, y)`
Tune multiple models simultaneously.

**Parameters:**
- `models_dict`: Dictionary of models to tune
- `X`: Feature matrix
- `y`: Target variable

**Returns:** `Dict` of tuning results for each model

**Example:**
```python
models = {
    'RandomForest': RandomForestClassifier(),
    'LogisticRegression': LogisticRegression()
}
results = tuner.tune_multiple_models(models, X_train, y_train)
```

## Tuning Strategies

### Supported Search Types
1. **Grid Search**
   - Exhaustive search over specified parameter values
   - Suitable for smaller parameter spaces

2. **Random Search**
   - Randomly samples parameter configurations
   - More efficient for large parameter spaces

3. **Bayesian Optimization**
   - Intelligent search using probabilistic model
   - Adapts search based on previous results

4. **Hyperopt**
   - Advanced probabilistic hyperparameter optimization
   - Supports complex search spaces

## Parameter Grid Generation

### Automatic Parameter Grid
Generates model-specific parameter grids based on:
- Model type
- Problem type (classification/regression)
- Known best practices

**Example Parameter Grids:**
```python
# Random Forest Classification Grid
{
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [5, 10, 20, None],
    'min_samples_split': [2, 5, 10],
    'max_features': ['sqrt', 'log2', None]
}

# Logistic Regression Grid
{
    'C': [0.001, 0.01, 0.1, 1.0, 10.0],
    'penalty': ['l1', 'l2'],
    'solver': ['liblinear', 'saga']
}
```

## Advanced Usage

### Comprehensive Tuning Workflow
```python
from automl import HyperparameterTuner
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Initialize tuner
tuner = HyperparameterTuner(
    problem_type='classification',
    cv=5,
    n_jobs=-1
)

# Tune a specific model
results = tuner.tune_model(
    'RandomForest',
    RandomForestClassifier(),
    X_train,
    y_train,
    search_type='bayesian',  # 'grid', 'random', 'bayesian', 'hyperopt'
    n_iter=50  # Number of iterations for random/bayesian search
)

# Get tuning summary
summary = tuner.get_tuning_summary()
print(summary)

# Get best parameters
best_params = results['best_params']
best_score = results['best_score']
```

## Visualization Methods

### `plot_tuning_results(model_name, param1, param2=None)`
Visualize hyperparameter tuning results.

**Parameters:**
- `model_name`: Model to visualize
- `param1`: First parameter for plotting
- `param2`: Optional second parameter for heatmap

**Example:**
```python
tuner.plot_tuning_results(
    'RandomForest',
    'n_estimators',
    'max_depth'
)
```

### `plot_parameter_importance(model_name)`
Analyze parameter importance based on correlation with model performance.

**Parameters:**
- `model_name`: Model to analyze

**Example:**
```python
tuner.plot_parameter_importance('RandomForest')
```

## Performance Considerations
- Parallel processing support
- Efficient search algorithms
- Configurable computational resources
- Caching of intermediate results

## Error Handling
- Comprehensive logging
- Fallback to default configurations
- Detailed error messages

## Compatibility
- Works with scikit-learn compatible models
- Supports various problem types
- Handles different model complexities

## Saving and Loading Results

### `save_tuning_results(directory, model_name=None)`
Save tuning results and best models.

**Parameters:**
- `directory`: Output directory
- `model_name`: Optional specific model to save

**Example:**
```python
tuner.save_tuning_results('tuning_output/')
```

### `load_tuning_results(directory, model_name)`
Load previously saved tuning results.

**Parameters:**
- `directory`: Directory with saved results
- `model_name`: Model to load

**Example:**
```python
loaded_results = tuner.load_tuning_results(
    'tuning_output/',
    'RandomForest'
)
```

## Example Full Workflow
```python
from automl import HyperparameterTuner
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create tuner
tuner = HyperparameterTuner(problem_type='classification')

# Tune models
models = {
    'RandomForest': RandomForestClassifier()
}
results = tuner.tune_multiple_models(models, X_train, y_train)

# Analyze results
summary = tuner.get_tuning_summary()
print(summary)
```

---

<div align="center">
🚀 **Intelligent Hyperparameter Optimization** 🧠
</div>
