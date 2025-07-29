# Data Preprocessing in Machine Learning

## 🌟 Introduction to Preprocessing

Data preprocessing is a critical step in machine learning that transforms raw data into a format suitable for model training. Effective preprocessing can significantly improve model performance, reduce overfitting, and enhance generalization.

## 🧩 Preprocessing Fundamentals

### Why Preprocessing Matters
- Standardizes feature scales
- Handles missing values
- Reduces noise
- Improves model performance
- Enables better feature comparisons

## 🔧 Core Preprocessing Techniques

### 1. Scaling Techniques
```python
from sklearn.preprocessing import (
    StandardScaler,      # Z-score normalization
    MinMaxScaler,        # Scales to fixed range
    RobustScaler         # Less sensitive to outliers
)

# Standard Scaling (Zero mean, unit variance)
standard_scaler = StandardScaler()
X_scaled = standard_scaler.fit_transform(X)

# Min-Max Scaling (0-1 range)
minmax_scaler = MinMaxScaler()
X_normalized = minmax_scaler.fit_transform(X)
```

### 2. Handling Missing Values
```python
import numpy as np
import pandas as pd

def handle_missing_values(X):
    """
    Strategies for handling missing data

    Args:
        X: Input data with missing values

    Returns:
        Processed data with handled missing values
    """
    # Simple imputation strategies

    # Mean/Median Imputation
    X_mean_imputed = np.nan_to_num(X, nan=np.nanmean(X))

    # Pandas DataFrame Handling
    if isinstance(X, pd.DataFrame):
        # Fill numeric columns with median
        X_numeric = X.select_dtypes(include=[np.number])
        X_numeric.fillna(X_numeric.median(), inplace=True)

        # Fill categorical columns with mode
        X_categorical = X.select_dtypes(exclude=[np.number])
        X_categorical.fillna(X_categorical.mode().iloc[0], inplace=True)

    return X_mean_imputed
```

### 3. Encoding Categorical Variables
```python
from sklearn.preprocessing import (
    OneHotEncoder,       # Creates binary columns
    OrdinalEncoder,      # Converts to integer labels
    LabelEncoder         # Converts to single column
)

# One-Hot Encoding
onehot_encoder = OneHotEncoder(sparse=False)
X_encoded = onehot_encoder.fit_transform(categorical_data)

# Ordinal Encoding (Preserves order)
ordinal_encoder = OrdinalEncoder()
X_ordinal = ordinal_encoder.fit_transform(categorical_data)
```

### 4. Feature Engineering
```python
from sklearn.preprocessing import PolynomialFeatures

def create_interaction_features(X):
    """
    Generate polynomial and interaction features

    Args:
        X: Original feature matrix

    Returns:
        Expanded feature matrix with interactions
    """
    # Create polynomial features
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)

    return X_poly
```

## 🤖 Custom Preprocessor Implementation

### Base Preprocessor Class
```python
from abc import ABC, abstractmethod

class BasePreprocessor(ABC):
    @abstractmethod
    def fit(self, X, y=None):
        """
        Learn preprocessing parameters from data

        Args:
            X: Input features
            y: Optional target variable
        """
        pass

    @abstractmethod
    def transform(self, X):
        """
        Apply preprocessing to input data

        Args:
            X: Input features

        Returns:
            Transformed features
        """
        pass

    def fit_transform(self, X, y=None):
        """
        Fit preprocessor and transform in one step

        Args:
            X: Input features
            y: Optional target variable

        Returns:
            Transformed features
        """
        return self.fit(X, y).transform(X)
```

### Advanced Custom Preprocessor
```python
class AdvancedPreprocessor(BasePreprocessor):
    def __init__(self, scaling=True, encoding=True):
        self.scaling = StandardScaler() if scaling else None
        self.encoding = OneHotEncoder(sparse=False) if encoding else None

    def fit(self, X, y=None):
        # Separate numeric and categorical columns
        if isinstance(X, pd.DataFrame):
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            categorical_cols = X.select_dtypes(exclude=[np.number]).columns

            if self.scaling:
                self.scaling.fit(X[numeric_cols])

            if self.encoding:
                self.encoding.fit(X[categorical_cols])

        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            categorical_cols = X.select_dtypes(exclude=[np.number]).columns

            # Transform numeric columns
            if self.scaling:
                X[numeric_cols] = self.scaling.transform(X[numeric_cols])

            # Transform categorical columns
            if self.encoding:
                encoded_cats = self.encoding.transform(X[categorical_cols])
                encoded_df = pd.DataFrame(
                    encoded_cats,
                    columns=self.encoding.get_feature_names_out(categorical_cols)
                )
                X = pd.concat([X.drop(columns=categorical_cols), encoded_df], axis=1)

            return X.values

        return X
```

## 🔬 Preprocessing Pipeline

### Combining Multiple Preprocessing Steps
```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def create_preprocessing_pipeline(numeric_features, categorical_features):
    """
    Create a comprehensive preprocessing pipeline

    Args:
        numeric_features: List of numeric column names
        categorical_features: List of categorical column names

    Returns:
        Preprocessing pipeline
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    return preprocessor
```

## 🚀 Best Practices

1. Understand your data
2. Handle missing values
3. Scale numeric features
4. Encode categorical variables
5. Create interaction features
6. Avoid data leakage
7. Use cross-validation

## 📊 Example Preprocessing Workflow
```python
from automl import AutoML

# Prepare your data
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Initialize AutoML with custom preprocessor
automl = AutoML(
    problem_type='classification',
    preprocessor=AdvancedPreprocessor()
)

# Train and evaluate
automl.fit(X_train, y_train)
results = automl.evaluate(X_test, y_test)
```

---

<div align="center">
🧠 **Transform Data, Unlock Model Potential** 🚀

*Preprocessing is the foundation of successful machine learning*
</div>
