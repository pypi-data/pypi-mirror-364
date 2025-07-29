# Quick Start Guide for AutoML Framework

## 🚀 Getting Started

This guide will help you quickly start using the AutoML Framework with simple, practical examples.

## Prerequisites
- Installed AutoML Framework
- Basic Python knowledge
- scikit-learn datasets (optional, but recommended for examples)

## 1. Basic Classification Example

### Simple Iris Dataset Classification
```python
from automl import AutoML
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load iris dataset
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize AutoML for classification
automl = AutoML(problem_type='classification')

# Train models
automl.fit(X_train, y_train)

# Evaluate models
results = automl.evaluate(X_test, y_test)

# Get performance leaderboard
leaderboard = automl.get_leaderboard()
print(leaderboard)

# Make predictions with best model
predictions = automl.predict(X_test)
```

## 2. Regression Example

### Boston Housing Price Prediction
```python
from automl import AutoML
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

# Load boston housing dataset
X, y = load_boston(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize AutoML for regression
automl = AutoML(problem_type='regression')

# Train and evaluate
automl.fit(X_train, y_train)
results = automl.evaluate(X_test, y_test)

# Get best model predictions
predictions = automl.predict(X_test)
```

## 3. Advanced Overfitting Control

### Detecting and Mitigating Overfitting
```python
# Configure overfitting detection
automl.pipeline.set_overfitting_control(
    detection_enabled=True,  # Enable detection
    auto_mitigation=True,    # Automatically mitigate
    threshold=0.3            # Sensitivity level
)

# Get overfitting assessment
assessment = automl.get_overfitting_assessment()
print("Overfitting Severity:", assessment['severity'])

# Get improvement suggestions
suggestions = automl.get_improvement_suggestions()
print("Improvement Suggestions:", suggestions)
```

## 4. Hyperparameter Tuning

### Advanced Model Optimization
```python
from automl import TuningIntegrator

# Create tuning integrator
tuner = TuningIntegrator(automl)

# Advanced model tuning
summary = tuner.tune_models(
    X_train, y_train,
    search_type='bayesian',  # Can be 'grid', 'random', 'bayesian'
    n_iter=50,               # Number of iterations
    register_best=True       # Automatically register best models
)
```

## 5. Model Persistence

### Saving and Loading Models
```python
# Save the best model
automl.save_best_model('best_model.pkl')

# Load a saved model
loaded_model = automl.load_model('best_model.pkl')
```

## 6. Feature Importance

### Analyzing Model Features
```python
# Get feature importance
feature_importance = automl.get_feature_importance()
print("Top Features:", feature_importance)
```

## Common Patterns and Best Practices

### Handling Different Datasets
- Always split data into train and test sets
- Normalize or scale features if needed
- Use appropriate problem type ('classification' or 'regression')

### Performance Optimization
- Increase `n_iter` for more thorough hyperparameter search
- Use cross-validation for robust model evaluation
- Monitor overfitting metrics

## Troubleshooting

### Common Issues
- Ensure compatible Python version (3.8+)
- Check data preprocessing
- Verify data shape and type

### Getting Help
- Check [documentation](README.md)
- Open GitHub issues
- Consult error messages

## Next Steps
- Explore [Advanced Usage](advanced_usage.md)
- Check [API Documentation](api/README.md)
- Experiment with your own datasets

---

<div align="center">
🚀 **Automate Your Machine Learning Journey** 🤖
</div>
