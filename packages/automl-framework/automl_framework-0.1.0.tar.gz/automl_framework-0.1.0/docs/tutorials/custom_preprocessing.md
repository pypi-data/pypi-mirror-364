# Custom Preprocessing Tutorial

## 🌟 Mastering Data Transformation in AutoML Framework

This tutorial explores the art of creating custom preprocessors, enabling you to transform your data precisely for machine learning models.

## 📋 Prerequisites
- Basic Python knowledge
- Understanding of data preprocessing
- AutoML Framework installed
  ```bash
  pip install automl-framework
  ```

## 🧠 Tutorial Objectives
- Create custom preprocessors
- Handle complex data transformations
- Integrate with AutoML workflow
- Solve real-world preprocessing challenges

## 1. 🔬 Preprocessor Fundamentals

### Base Preprocessor Interface
```python
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class BasePreprocessor(ABC):
    @abstractmethod
    def fit(self, X, y=None):
        """Learn preprocessing parameters"""
        pass

    @abstractmethod
    def transform(self, X):
        """Apply data transformation"""
        pass

    def fit_transform(self, X, y=None):
        """Fit and transform in one step"""
        return self.fit(X, y).transform(X)
```

## 2. 🧩 Simple Custom Preprocessor

### Handling Specific Data Challenges
```python
class SpecialScaler(BasePreprocessor):
    def __init__(self, columns=None, method='log'):
        """
        Custom scaling with multiple transformation options

        Args:
            columns: Specific columns to transform
            method: Transformation method ('log', 'sqrt', 'boxcox')
        """
        self.columns = columns
        self.method = method
        self.fitted_params = {}

    def fit(self, X, y=None):
        # Determine columns to transform
        if self.columns is None:
            if isinstance(X, pd.DataFrame):
                self.columns = X.select_dtypes(include=[np.number]).columns
            else:
                self.columns = range(X.shape[1])

        # Learn transformation parameters
        for col in self.columns:
            column_data = X[:, col] if not isinstance(X, pd.DataFrame) else X[col]

            if self.method == 'log':
                # Handle non-positive values
                min_val = np.min(column_data)
                self.fitted_params[col] = min_val if min_val <= 0 else 0

            elif self.method == 'sqrt':
                self.fitted_params[col] = 0

            elif self.method == 'boxcox':
                from scipy import stats
                # Shift data to make it positive
                shifted_data = column_data + abs(np.min(column_data)) + 1
                _, fitted_lambda = stats.boxcox(shifted_data)
                self.fitted_params[col] = fitted_lambda

        return self

    def transform(self, X):
        # Create a copy to avoid modifying original data
        X_transformed = X.copy() if isinstance(X, pd.DataFrame) else X.copy()

        for col in self.columns:
            column_data = X_transformed[:, col] if not isinstance(X_transformed, pd.DataFrame) else X_transformed[col]

            if self.method == 'log':
                column_data = np.log(column_data + abs(self.fitted_params[col]) + 1)

            elif self.method == 'sqrt':
                column_data = np.sqrt(column_data)

            elif self.method == 'boxcox':
                from scipy import stats
                column_data = stats.boxcox(
                    column_data + abs(np.min(column_data)) + 1,
                    lmbda=self.fitted_params[col]
                )

            # Update transformed data
            if isinstance(X_transformed, pd.DataFrame):
                X_transformed[col] = column_data
            else:
                X_transformed[:, col] = column_data

        return X_transformed
```

## 3. 🚀 Advanced Preprocessing Example

### Comprehensive Data Transformation
```python
from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder,
    RobustScaler
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

class AdvancedPreprocessor(BasePreprocessor):
    def __init__(
        self,
        numeric_features=None,
        categorical_features=None,
        impute_strategy='median'
    ):
        """
        Comprehensive data preprocessing pipeline

        Args:
            numeric_features: List of numeric column names/indices
            categorical_features: List of categorical column names/indices
            impute_strategy: Strategy for handling missing values
        """
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.impute_strategy = impute_strategy

        # Create preprocessing pipeline
        self.preprocessor = None

    def _build_preprocessor(self, X):
        """
        Dynamically build preprocessing pipeline

        Args:
            X: Input data to infer feature types
        """
        # Infer feature types if not provided
        if self.numeric_features is None or self.categorical_features is None:
            if isinstance(X, pd.DataFrame):
                self.numeric_features = X.select_dtypes(include=[np.number]).columns
                self.categorical_features = X.select_dtypes(exclude=[np.number]).columns
            else:
                # Assume all features are numeric for numpy arrays
                self.numeric_features = range(X.shape[1])
                self.categorical_features = []

        # Create preprocessing components
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy=self.impute_strategy)),
            ('scaler', RobustScaler())  # More robust to outliers
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        # Combine transformers
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ])

        return self

    def fit(self, X, y=None):
        """
        Learn preprocessing parameters

        Args:
            X: Input features
            y: Optional target variable

        Returns:
            Self
        """
        # Build preprocessor if not already created
        self._build_preprocessor(X)

        # Fit the preprocessor
        self.preprocessor.fit(X)

        return self

    def transform(self, X):
        """
        Apply preprocessing to input data

        Args:
            X: Input features

        Returns:
            Transformed features
        """
        # Ensure preprocessor is created
        if self.preprocessor is None:
            self._build_preprocessor(X)

        # Transform data
        return self.preprocessor.transform(X)

## 4. 🔍 Practical Use Cases

### Handling Complex Datasets
```python
import pandas as pd
import numpy as np
from automl import AutoML

# Example complex dataset
def create_sample_dataset():
    """Create a sample dataset with mixed feature types"""
    np.random.seed(42)

    # Numeric features with different scales and distributions
    numeric_data = pd.DataFrame({
        'income': np.random.lognormal(mean=10, sigma=1, size=1000),
        'age': np.random.normal(40, 10, 1000),
        'experience': np.random.poisson(5, 1000)
    })

    # Categorical features
    categorical_data = pd.DataFrame({
        'education': np.random.choice(
            ['high_school', 'bachelors', 'masters', 'phd'],
            size=1000
        ),
        'industry': np.random.choice(
            ['tech', 'finance', 'healthcare', 'education', 'other'],
            size=1000
        )
    })

    # Combine datasets
    data = pd.concat([numeric_data, categorical_data], axis=1)

    # Create target variable (example classification)
    data['high_income'] = (data['income'] > data['income'].median()).astype(int)

    return data

# Load and prepare dataset
dataset = create_sample_dataset()
X = dataset.drop('high_income', axis=1)
y = dataset['high_income']

# Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create AutoML with custom preprocessor
automl = AutoML(problem_type='classification')

# Register model with advanced preprocessor
advanced_preprocessor = AdvancedPreprocessor(
    numeric_features=['income', 'age', 'experience'],
    categorical_features=['education', 'industry']
)

automl.register_model(
    'ComplexDataModel',
    RandomForestClassifier(),
    preprocessor=advanced_preprocessor
)

# Train and evaluate
automl.fit(X_train, y_train)
results = automl.evaluate(X_test, y_test)
```

## 5. 🛠️ Preprocessing Techniques Showcase

### Transformation Strategies
```python
class MultiTransformPreprocessor(BasePreprocessor):
    def __init__(self, transformations=None):
        """
        Apply multiple transformations to different feature groups

        Args:
            transformations: Dict mapping feature groups to transformation methods
        """
        self.transformations = transformations or {
            'log': ['income', 'sales'],
            'sqrt': ['age', 'experience'],
            'robust_scale': ['numeric_features']
        }
        self.transformation_objects = {}

    def fit(self, X, y=None):
        # Apply different transformations to feature groups
        for transform_type, features in self.transformations.items():
            if transform_type == 'log':
                self.transformation_objects['log'] = LogTransformer(features)
                self.transformation_objects['log'].fit(X[features])

            elif transform_type == 'sqrt':
                self.transformation_objects['sqrt'] = SqrtTransformer(features)
                self.transformation_objects['sqrt'].fit(X[features])

            elif transform_type == 'robust_scale':
                self.transformation_objects['robust_scale'] = RobustScaler()
                self.transformation_objects['robust_scale'].fit(X[features])

        return self

    def transform(self, X):
        # Create a copy of input data
        X_transformed = X.copy()

        # Apply transformations
        for transform_type, transformer in self.transformation_objects.items():
            features = self.transformations[transform_type]
            X_transformed[features] = transformer.transform(X[features])

        return X_transformed

# Custom transformation helpers
class LogTransformer:
    def __init__(self, columns):
        self.columns = columns
        self.min_values = {}

    def fit(self, X):
        for col in self.columns:
            # Ensure log transformation works
            self.min_values[col] = max(0, -X[col].min() + 1)
        return self

    def transform(self, X):
        X_transformed = X.copy()
        for col in self.columns:
            X_transformed[col] = np.log(X_transformed[col] + self.min_values[col])
        return X_transformed

class SqrtTransformer:
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X):
        return self

    def transform(self, X):
        X_transformed = X.copy()
        for col in self.columns:
            X_transformed[col] = np.sqrt(X_transformed[col])
        return X_transformed
```

## 🎓 Learning Objectives
- ✅ Create custom preprocessors
- ✅ Handle complex data transformations
- ✅ Integrate with AutoML workflow
- ✅ Solve real-world preprocessing challenges

## 🚀 Best Practices
1. Understand your data's characteristics
2. Choose appropriate transformations
3. Handle edge cases (e.g., non-positive values)
4. Validate preprocessing results
5. Consider computational efficiency

## 💡 Advanced Challenges
- Implement feature interaction transformations
- Create domain-specific preprocessing
- Handle time series data
- Develop adaptive preprocessing techniques

## 🔍 Recommended Next Steps
- Experiment with your own datasets
- Combine multiple transformation techniques
- Analyze impact of different preprocessing methods
- Share your custom preprocessors with the community

---

<div align="center">
🌟 **Transform Your Data, Elevate Your Models** 🧠

*Preprocessing is an art and a science*
</div>
