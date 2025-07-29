# Metrics Calculator API Reference

## Overview
The Metrics Calculator provides comprehensive performance evaluation capabilities for machine learning models across different problem types.

## Class Signature
```python
class MetricsCalculator:
    def __init__(
        self,
        problem_type: str = 'classification'
    )
```

## Constructor Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `problem_type` | `str` | 'classification' or 'regression' | 'classification' |

## Key Methods

### `calculate_metrics(y_true, y_pred, y_pred_proba=None)`
Calculate performance metrics based on problem type.

**Parameters:**
- `y_true`: True target values
- `y_pred`: Predicted values
- `y_pred_proba`: Predicted probabilities (optional)

**Returns:** `Dict` of performance metrics

**Example:**
```python
metrics = metrics_calculator.calculate_metrics(
    y_true,
    y_pred,
    y_pred_proba
)
```

## Classification Metrics

### Supported Metrics
- Accuracy
- F1 Score
- Precision
- Recall
- ROC AUC

**Example Metrics Dictionary:**
```python
{
    'accuracy': 0.95,
    'f1_score': 0.94,
    'precision': 0.93,
    'recall': 0.95,
    'roc_auc': 0.97  # For binary classification
}
```

## Regression Metrics

### Supported Metrics
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- R² Score

**Example Metrics Dictionary:**
```python
{
    'mse': 0.05,
    'rmse': 0.22,
    'mae': 0.15,
    'r2': 0.93
}
```

## Advanced Usage

### Detailed Classification Reporting
```python
class MetricsCalculator:
    def get_classification_report(self, y_true, y_pred):
        """
        Generate comprehensive classification report

        Returns:
            Detailed text report of model performance
        """
        pass

# Example
report = metrics_calculator.get_classification_report(y_true, y_pred)
print(report)
```

## Multiclass and Binary Classification Handling

### Metric Calculation Strategies
- Binary Classification: Default metrics
- Multiclass Classification: Weighted average metrics

**Multiclass Metric Example:**
```python
# Handles both binary and multiclass problems
metrics = metrics_calculator.calculate_metrics(
    y_true_multiclass,
    y_pred_multiclass,
    y_pred_proba_multiclass
)
```

## Performance Visualization

### Metric Visualization Methods
```python
def plot_classification_metrics(y_true, y_pred, y_pred_proba):
    """
    Visualize classification performance metrics

    Creates:
    - Confusion Matrix
    - ROC Curve
    - Precision-Recall Curve
    """
    pass

def plot_regression_metrics(y_true, y_pred):
    """
    Visualize regression performance metrics

    Creates:
    - Actual vs Predicted Plot
    - Residual Plot
    - Error Distribution
    """
    pass
```

## Error Handling and Robustness

### Metric Calculation Safeguards
- Handles different input types
- Manages edge cases
- Provides informative error messages

**Robust Metric Calculation:**
```python
def robust_metric_calculation(y_true, y_pred, y_pred_proba=None):
    """
    Robust metric calculation with comprehensive error handling

    Handles:
    - Different array types
    - Partial predictions
    - Incompatible shapes
    """
    try:
        metrics = calculate_metrics(y_true, y_pred, y_pred_proba)
        return metrics
    except Exception as e:
        logger.error(f"Metric calculation error: {e}")
        return None
```

## Example Comprehensive Workflow
```python
from automl import MetricsCalculator
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Calculate metrics
metrics_calc = MetricsCalculator(problem_type='classification')
metrics = metrics_calc.calculate_metrics(y_test, y_pred, y_pred_proba)

# Generate classification report
report = metrics_calc.get_classification_report(y_test, y_pred)
print("Performance Metrics:", metrics)
print("\nDetailed Report:\n", report)
```

## Compatibility and Extensibility
- Works with scikit-learn compatible models
- Supports numpy arrays and pandas Series
- Easily extendable metric calculation

---

<div align="center">
🚀 **Comprehensive Model Performance Analysis** 🧠
</div>
