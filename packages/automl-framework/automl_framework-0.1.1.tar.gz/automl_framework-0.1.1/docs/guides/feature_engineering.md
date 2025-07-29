# Comprehensive Guide to Feature Engineering

## 🌟 Introduction to Feature Engineering

Feature engineering is the art and science of transforming raw data into meaningful features that improve machine learning model performance.

## 🧠 Core Concepts

### Feature Engineering Objectives
- Improve model accuracy
- Reduce dimensionality
- Capture complex relationships
- Enhance model interpretability

## 🔧 Feature Transformation Techniques

### 1. Numerical Feature Transformations
```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    QuantileTransformer
)

class AdvancedNumericalTransformer:
    """
    Comprehensive numerical feature transformation toolkit
    """
    def __init__(self, transformations=None):
        """
        Initialize feature transformations

        Args:
            transformations: Dict of transformation strategies
        """
        self.default_transformations = {
            'log': lambda x: np.log1p(x),
            'sqrt': np.sqrt,
            'square': np.square,
            'exp': np.exp,
            'box_cox': self._safe_box_cox,
            'yeo_johnson': self._safe_yeo_johnson
        }

        self.transformations = transformations or self.default_transformations
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler(),
            'quantile': QuantileTransformer(output_distribution='normal')
        }

    def _safe_box_cox(self, x, lmbda=None):
        """
        Safe Box-Cox transformation

        Args:
            x: Input array
            lmbda: Transformation parameter

        Returns:
            Transformed array
        """
        from scipy import stats

        # Ensure positive values
        x_positive = x - x.min() + 1

        # Compute optimal lambda if not provided
        if lmbda is None:
            _, lmbda = stats.boxcox(x_positive)

        return stats.boxcox(x_positive, lmbda=lmbda)

    def _safe_yeo_johnson(self, x, lmbda=None):
        """
        Safe Yeo-Johnson transformation

        Args:
            x: Input array
            lmbda: Transformation parameter

        Returns:
            Transformed array
        """
        from scipy import stats

        if lmbda is None:
            # Estimate optimal lambda
            _, lmbda = stats.yeojohnson(x)

        return stats.yeojohnson(x, lmbda=lmbda)

    def transform(self, X, columns=None):
        """
        Apply multiple transformations

        Args:
            X: Input DataFrame or array
            columns: Specific columns to transform

        Returns:
            Transformed features
        """
        X_transformed = X.copy() if isinstance(X, pd.DataFrame) else X.copy()

        # Determine columns to transform
        if columns is None:
            columns = X.columns if isinstance(X, pd.DataFrame) else range(X.shape[1])

        # Apply transformations
        for col in columns:
            for name, transform_func in self.transformations.items():
                try:
                    transformed_col = transform_func(X[col] if isinstance(X, pd.DataFrame) else X[:, col])

                    # Add transformed column
                    new_col_name = f'{col}_{name}_transformed'
                    if isinstance(X, pd.DataFrame):
                        X_transformed[new_col_name] = transformed_col
                    else:
                        X_transformed = np.column_stack([X_transformed, transformed_col])
                except Exception as e:
                    print(f"Transformation {name} failed for column {col}: {e}")

        return X_transformed
```

### 2. Categorical Feature Engineering
```python
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    LabelEncoder
)

class AdvancedCategoricalEncoder:
    """
    Advanced categorical feature encoding techniques
    """
    def __init__(self, encoding_strategy='auto'):
        """
        Initialize categorical encoder

        Args:
            encoding_strategy: Encoding method
        """
        self.encoding_strategy = encoding_strategy
        self.encoders = {}

    def fit_transform(self, X, columns=None):
        """
        Fit and transform categorical features

        Args:
            X: Input DataFrame
            columns: Specific columns to encode

        Returns:
            Transformed categorical features
        """
        # Determine columns to encode
        if columns is None:
            columns = X.select_dtypes(include=['object', 'category']).columns

        X_transformed = X.copy()

        for col in columns:
            # Determine encoding strategy
            if self.encoding_strategy == 'auto':
                strategy = self._determine_encoding_strategy(X[col])
            else:
                strategy = self.encoding_strategy

            # Apply encoding
            if strategy == 'onehot':
                encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
                encoded = encoder.fit_transform(X[[col]])

                # Create column names
                onehot_cols = [f'{col}_{cat}' for cat in encoder.categories_[0]]
                X_transformed[onehot_cols] = encoded
                X_transformed.drop(columns=[col], inplace=True)

                self.encoders[col] = encoder

            elif strategy == 'ordinal':
                encoder = OrdinalEncoder()
                X_transformed[col] = encoder.fit_transform(X[[col]])
                self.encoders[col] = encoder

            elif strategy == 'label':
                encoder = LabelEncoder()
                X_transformed[col] = encoder.fit_transform(X[col])
                self.encoders[col] = encoder

        return X_transformed

    def _determine_encoding_strategy(self, series):
        """
        Determine best encoding strategy

        Args:
            series: Categorical series

        Returns:
            Recommended encoding strategy
        """
        unique_count = series.nunique()

        if unique_count <= 2:
            return 'label'
        elif unique_count <= 10:
            return 'onehot'
        else:
            return 'ordinal'
```

### 3. Advanced Feature Generation
```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures

class FeatureGenerator:
    """
    Advanced feature generation and interaction techniques
    """
    def __init__(self, interaction_level=2):
        """
        Initialize feature generator

        Args:
            interaction_level: Depth of feature interactions
        """
        self.interaction_level = interaction_level
        self.feature_generators = {}

    def generate_polynomial_features(self, X, columns=None):
        """
        Create polynomial and interaction features

        Args:
            X: Input features
            columns: Specific columns to generate features for

        Returns:
            DataFrame with generated features
        """
        # Determine columns to use
        if columns is None:
            columns = (X.select_dtypes(include=[np.number]).columns
                       if isinstance(X, pd.DataFrame)
                       else range(X.shape[1]))

        # Select numeric columns
        if isinstance(X, pd.DataFrame):
            X_numeric = X[columns]
        else:
            X_numeric = X[:, columns]

        # Generate polynomial features
        poly = PolynomialFeatures(
            degree=self.interaction_level,
            include_bias=False
        )
        poly_features = poly.fit_transform(X_numeric)

        # Create feature names
        feature_names = poly.get_feature_names_out(
            input_features=columns if isinstance(columns, list)
            else [str(col) for col in columns]
        )

        # Convert to DataFrame if input was DataFrame
        if isinstance(X, pd.DataFrame):
            return pd.DataFrame(
                poly_features,
                columns=feature_names,
                index=X.index
            )

        return poly_features

    def create_interaction_features(self, X):
        """
        Generate interaction features between different columns

        Args:
            X: Input features

        Returns:
            DataFrame with interaction features
        """
        X_transformed = X.copy() if isinstance(X, pd.DataFrame) else X.copy()

        # Numeric columns for interactions
        numeric_cols = (X.select_dtypes(include=[np.number]).columns
                        if isinstance(X, pd.DataFrame)
                        else range(X.shape[1]))

        # Create pairwise interactions
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                # Different interaction types
                interaction_features = {
                    'product': self._multiply_columns(X, col1, col2),
                    'ratio': self._divide_columns(X, col1, col2),
                    'difference': self._subtract_columns(X, col1, col2)
                }

                # Add interaction features
                for interaction_type, feature in interaction_features.items():
                    col_name = f'{col1}_{interaction_type}_{col2}'
                    if isinstance(X, pd.DataFrame):
                        X_transformed[col_name] = feature
                    else:
                        X_transformed = np.column_stack([X_transformed, feature])

        return X_transformed

    def _multiply_columns(self, X, col1, col2):
        """Multiply two columns"""
        return (X[col1] * X[col2]) if isinstance(X, pd.DataFrame) else X[:, col1] * X[:, col2]

    def _divide_columns(self, X, col1, col2):
        """Divide columns with safe handling of zero division"""
        if isinstance(X, pd.DataFrame):
            return X[col1] / (X[col2] + 1e-8)
        else:
            return X[:, col1] / (X[:, col2] + 1e-8)

    def _subtract_columns(self, X, col1, col2):
        """Subtract columns"""
        return (X[col1] - X[col2]) if isinstance(X, pd.DataFrame) else X[:, col1] - X[:, col2]

def advanced_feature_engineering_pipeline(X, y=None):
    """
    Comprehensive feature engineering pipeline

    Args:
        X: Input features
        y: Optional target variable for supervised feature generation

    Returns:
        Engineered feature matrix
    """
    # Numerical transformations
    num_transformer = AdvancedNumericalTransformer()
    X_numeric_transformed = num_transformer.transform(X)

    # Categorical encoding
    cat_encoder = AdvancedCategoricalEncoder()
    X_cat_encoded = cat_encoder.fit_transform(X)

    # Feature generation
    feature_generator = FeatureGenerator()

    # Polynomial features
    X_poly = feature_generator.generate_polynomial_features(X_numeric_transformed)

    # Interaction features
    X_interactions = feature_generator.create_interaction_features(X_numeric_transformed)

    # Combine all features
    if isinstance(X, pd.DataFrame):
        X_engineered = pd.concat([
            X_numeric_transformed,
            X_cat_encoded,
            X_poly,
            X_interactions
        ], axis=1)
    else:
        X_engineered = np.column_stack([
            X_numeric_transformed,
            X_cat_encoded,
            X_poly,
            X_interactions
        ])

    return X_engineered
```

## 4. Feature Selection Techniques
```python
from sklearn.feature_selection import (
    SelectKBest,
    f_classif,
    mutual_info_classif,
    RFE,
    SelectFromModel
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

class AdvancedFeatureSelector:
    """
    Comprehensive feature selection strategies
    """
    def __init__(self, problem_type='classification'):
        """
        Initialize feature selector

        Args:
            problem_type: Type of machine learning problem
        """
        self.problem_type = problem_type
        self.feature_selectors = {}

    def select_features(self, X, y, method='auto', n_features=None):
        """
        Select most important features

        Args:
            X: Feature matrix
            y: Target variable
            method: Feature selection method
            n_features: Number of features to select

        Returns:
            Selected feature matrix
        """
        # Determine number of features
        if n_features is None:
            n_features = min(X.shape[1] // 2, 10)

        # Select feature selection method
        if method == 'auto':
            method = self._recommend_selection_method()

        # Feature selection methods
        selection_methods = {
            'univariate': self._univariate_feature_selection,
            'recursive': self._recursive_feature_elimination,
            'model_based': self._model_based_selection,
            'mutual_info': self._mutual_information_selection
        }

        # Apply selected method
        selector_func = selection_methods.get(method, self._model_based_selection)
        selected_features, selector = selector_func(X, y, n_features)

        # Store selector for potential future use
        self.feature_selectors[method] = selector

        return selected_features

    def _recommend_selection_method(self):
        """
        Recommend feature selection method based on problem type

        Returns:
            Recommended selection method
        """
        method_recommendations = {
            'classification': 'univariate',
            'regression': 'model_based'
        }

        return method_recommendations.get(self.problem_type, 'model_based')

    def _univariate_feature_selection(self, X, y, n_features):
        """
        Univariate feature selection

        Args:
            X: Feature matrix
            y: Target variable
            n_features: Number of features to select

        Returns:
            Selected features and selector
        """
        # Select scoring function based on problem type
        scoring_func = f_classif if self.problem_type == 'classification' else f_regression

        selector = SelectKBest(score_func=scoring_func, k=n_features)
        X_selected = selector.fit_transform(X, y)

        return X_selected, selector

    def _recursive_feature_elimination(self, X, y, n_features):
        """
        Recursive feature elimination

        Args:
            X: Feature matrix
            y: Target variable
            n_features: Number of features to select

        Returns:
            Selected features and selector
        """
        # Select estimator based on problem type
        estimator = (RandomForestClassifier() if self.problem_type == 'classification'
                     else RandomForestRegressor())

        selector = RFE(estimator=estimator, n_features_to_select=n_features)
        X_selected = selector.fit_transform(X, y)

        return X_selected, selector

    def _model_based_selection(self, X, y, n_features):
        """
        Model-based feature selection

        Args:
            X: Feature matrix
            y: Target variable
            n_features: Number of features to select

        Returns:
            Selected features and selector
        """
        # Select estimator based on problem type
        estimator = (RandomForestClassifier() if self.problem_type == 'classification'
                     else RandomForestRegressor())

        selector = SelectFromModel(
            estimator,
            max_features=n_features,
            threshold='median'
        )
        X_selected = selector.fit_transform(X, y)

        return X_selected, selector

    def _mutual_information_selection(self, X, y, n_features):
        """
        Mutual information feature selection

        Args:
            X: Feature matrix
            y: Target variable
            n_features: Number of features to select

        Returns:
            Selected features and selector
        """
        selector = SelectKBest(
            score_func=(mutual_info_classif if self.problem_type == 'classification'
                        else mutual_info_regression),
            k=n_features
        )
        X_selected = selector.fit_transform(X, y)

        return X_selected, selector
```

## 🎓 Key Learning Objectives
- ✅ Understand feature transformation techniques
- ✅ Learn advanced feature generation strategies
- ✅ Master feature selection methods
- ✅ Improve model performance through feature engineering

## 🚀 Best Practices
1. Understand your data's characteristics
2. Experiment with multiple transformation techniques
3. Be cautious of feature explosion
4. Validate feature importance
5. Consider domain knowledge
6. Use feature selection to reduce complexity

## 💡 Advanced Challenges
- Develop domain-specific feature engineering techniques
- Create adaptive feature generation methods
- Implement automated feature selection
- Build meta-learning feature engineering approaches

## 🔍 Recommended Next Steps
- Experiment with different datasets
- Try various feature engineering techniques
- Analyze feature importance
- Share your feature engineering insights

---

<div align="center">
🌟 **Transform Your Data, Elevate Your Models** 🧠

*Feature engineering is thealchemy of machine learning*
</div>
