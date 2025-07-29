# Custom Models in AutoML Framework

## 🧩 Adding Your Own Models

### 1. Scikit-learn Compatible Models
```python
from automl import AutoML
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.svm import SVC

# Initialize AutoML
automl = AutoML(problem_type='classification')

# Register custom models
automl.register_model(
    'ExtraTrees',
    ExtraTreesClassifier(n_estimators=200)
)

automl.register_model(
    'CustomSVM',
    SVC(kernel='rbf', probability=True)
)

# Train with custom models
automl.fit(X_train, y_train)
```

### 2. Custom Preprocessor with Model
```python
from automl.preprocessors import StandardPreprocessor
from sklearn.preprocessing import RobustScaler

# Create custom preprocessor
custom_preprocessor = StandardPreprocessor()

# Register model with custom preprocessor
automl.register_model(
    'RobustModel',
    RandomForestClassifier(n_estimators=150),
    preprocessor=custom_preprocessor
)
```

### 3. Advanced Custom Model
```python
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np

class MyCustomClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, threshold=0.5):
        self.threshold = threshold

    def fit(self, X, y):
        # Custom training logic
        self.classes_ = np.unique(y)
        return self

    def predict(self, X):
        # Custom prediction logic
        probas = self._predict_proba(X)
        return np.where(probas > self.threshold, 1, 0)

    def predict_proba(self, X):
        # Implement probabilistic predictions
        return np.random.random(size=(X.shape[0], 2))

# Register custom model
automl.register_model(
    'MyCustomClassifier',
    MyCustomClassifier(threshold=0.6)
)
```

## 🔧 Model Registration Guidelines

### Compatibility Requirements
- Implement `fit()` method
- Implement `predict()` method
- Optional `predict_proba()` for classification
- Compatible with scikit-learn API

### Preprocessing Options
- Use built-in preprocessors
- Create custom preprocessors
- Handle different feature types

## 💡 Best Practices
- Ensure model is scikit-learn compatible
- Implement all required methods
- Handle different input types
- Consider performance implications

## 🚀 Advanced Techniques
- Ensemble custom models
- Create model wrappers
- Implement domain-specific logic
- Optimize for specific use cases

## 🎓 Learning Objectives
- ✅ Add custom models to AutoML
- ✅ Use custom preprocessors
- ✅ Extend framework capabilities
- ✅ Create domain-specific models

---

<div align="center">
🧠 **Extend AutoML, Your Way** 🚀

*Flexibility meets intelligence*
</div>
