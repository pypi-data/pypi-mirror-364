# Utilities API Reference

## Overview
The Utilities module provides helper functions and classes to support various machine learning tasks and data manipulation.

## DataUtils Class

### Class Signature
```python
class DataUtils:
    @staticmethod
    def train_test_split(X, y, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        pass

    @staticmethod
    def check_data_quality(X, y):
        """Analyze data quality and characteristics"""
        pass
```

## Key Methods

### `train_test_split(X, y, test_size=0.2, random_state=42)`
Split data into training and testing sets.

**Parameters:**
- `X`: Feature matrix
- `y`: Target variable
- `test_size`: Proportion of data for testing
- `random_state`: Random seed for reproducibility

**Returns:** Tuple of (X_train, X_test, y_train, y_test)

**Example:**
```python
from automl.utils import DataUtils

X_train, X_test, y_train, y_test = DataUtils.train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)
```

### `check_data_quality(X, y)`
Perform comprehensive data quality analysis.

**Parameters:**
- `X`: Feature matrix
- `y`: Target variable

**Returns:** `Dict` with data quality metrics

**Example:**
```python
quality_report = DataUtils.check_data_quality(X, y)
print("Missing Values:", quality_report['missing_values_X'])
print("Class Distribution:", quality_report['class_distribution'])
```

### Data Quality Report Details
```python
{
    'missing_values_X': int,  # Number of missing values in features
    'missing_values_y': int,  # Number of missing values in target
    'class_distribution': Dict[Any, float],  # Distribution of target classes
    'is_imbalanced': bool,  # Whether classes are imbalanced
    'zero_variance_features': List[str]  # Features with no variance
}
```

## Logging Utility

### `setup_logging(level='INFO')`
Configure logging for the AutoML framework.

**Parameters:**
- `level`: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

**Returns:** Configured logger

**Example:**
```python
from automl.utils import setup_logging

logger = setup_logging(level='DEBUG')
logger.info("AutoML process started")
```

## Advanced Data Manipulation

### Example of Advanced Data Checks
```python
from automl.utils import DataUtils
import numpy as np
import pandas as pd

def advanced_data_preprocessing(X, y):
    # Check data quality
    quality_report = DataUtils.check_data_quality(X, y)

    # Handle missing values
    if quality_report['missing_values_X'] > 0:
        X = handle_missing_values(X)

    # Remove zero variance features
    if quality_report['zero_variance_features']:
        X = remove_zero_variance_features(X, quality_report['zero_variance_features'])

    # Handle class imbalance
    if quality_report['is_imbalanced']:
        X, y = balance_classes(X, y)

    return X, y

def handle_missing_values(X):
    """Example missing value handling"""
    if isinstance(X, pd.DataFrame):
        return X.fillna(X.mean())
    elif isinstance(X, np.ndarray):
        return np.nan_to_num(X, nan=np.nanmean(X))
    return X

def remove_zero_variance_features(X, zero_var_features):
    """Remove features with no variance"""
    if isinstance(X, pd.DataFrame):
        return X.drop(columns=zero_var_features)
    elif isinstance(X, np.ndarray):
        mask = np.ones(X.shape[1], dtype=bool)
        for idx in zero_var_features:
            mask[idx] = False
        return X[:, mask]
    return X
```

## Performance Monitoring Utilities

### Memory and Time Tracking
```python
import time
import tracemalloc

def performance_wrapper(func):
    """Decorator to track function performance"""
    def wrapper(*args, **kwargs):
        # Start memory tracking
        tracemalloc.start()
        start_time = time.time()

        # Execute function
        result = func(*args, **kwargs)

        # Calculate performance metrics
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()

        # Stop tracking
        tracemalloc.stop()

        # Log performance
        print(f"Function: {func.__name__}")
        print(f"Execution Time: {end_time - start_time:.4f} seconds")
        print(f"Memory Usage: {current / 10**6:.2f} MB")
        print(f"Peak Memory: {peak / 10**6:.2f} MB")

        return result
    return wrapper
```

## Error Handling Utilities

### Robust Error Handling
```python
def robust_execution(func, *args, **kwargs):
    """
    Execute a function with comprehensive error handling

    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Tuple of (result, error)
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        error_info = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }
        return None, error_info
```

## Compatibility and Extensibility
- Works with numpy arrays and pandas DataFrames
- Supports various data types
- Easily extensible utility functions

## Example Comprehensive Workflow
```python
from automl.utils import DataUtils, setup_logging

# Setup logging
logger = setup_logging(level='INFO')

# Load data
X, y = load_dataset()

# Perform data quality check
quality_report = DataUtils.check_data_quality(X, y)
logger.info(f"Data Quality Report: {quality_report}")

# Split data
X_train, X_test, y_train, y_test = DataUtils.train_test_split(X, y)

# Preprocess data
X_train, y_train = advanced_data_preprocessing(X_train, y_train)
```

---

<div align="center">
🚀 **Empowering Data Preparation and Analysis** 🧠
</div>
