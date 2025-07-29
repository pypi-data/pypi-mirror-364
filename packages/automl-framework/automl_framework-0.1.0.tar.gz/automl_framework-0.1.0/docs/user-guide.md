# AutoML Framework User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Problem Types](#problem-types)
4. [Basic Workflow](#basic-workflow)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Introduction

The AutoML Framework is designed to simplify machine learning workflows by automating model selection, training, and evaluation. This guide will help you understand and leverage the framework's capabilities.

## Core Concepts

### Automated Machine Learning
AutoML automates the process of:
- Model selection
- Hyperparameter tuning
- Overfitting detection
- Performance evaluation

### Key Components
- **AutoML Class**: Primary interface for machine learning tasks
- **Model Registry**: Manages multiple model instances
- **Overfitting Handler**: Detects and mitigates model overfitting
- **Hyperparameter Tuner**: Optimizes model configurations

## Problem Types

The framework supports two primary problem types:

### Classification
Predicting categorical labels
```python
automl = AutoML(problem_type='classification')
```

#### Supported Classification Tasks
- Binary classification
- Multi-class classification
- Probabilistic predictions

### Regression
Predicting continuous numeric values
```python
automl = AutoML(problem_type='regression')
```

#### Supported Regression Tasks
- Linear prediction
- Non-linear prediction
- Time series forecasting

## Basic Workflow

### 1. Data Preparation
```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Load your dataset
X = ...  # Your features
y = ...  # Your target variable

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
```

### 2. Initialize AutoML
```python
from automl import AutoML

# Create AutoML instance
automl = AutoML(
    problem_type='classification',  # or 'regression'
    random_state=42
)
```

### 3. Train Models
```python
# Fit models to training data
automl.fit(X_train, y_train)
```

### 4. Evaluate Performance
```python
# Evaluate on test data
results = automl.evaluate(X_test, y_test)

# Get performance leaderboard
leaderboard = automl.get_leaderboard()
print(leaderboard)
```

### 5. Make Predictions
```python
# Predict using the best model
predictions = automl.predict(X_test)

# Get prediction probabilities (for classification)
probabilities = automl.predict_proba(X_test)
```

## Advanced Features

### Overfitting Control
```python
# Configure overfitting detection
automl.pipeline.set_overfitting_control(
    detection_enabled=True,    # Enable detection
    auto_mitigation=True,      # Automatically mitigate
    threshold=0.3              # Sensitivity level
)

# Get overfitting assessment
assessment = automl.get_overfitting_assessment()
print("Overfitting Severity:", assessment['severity'])

# Get improvement suggestions
suggestions = automl.get_improvement_suggestions()
print(suggestions)
```

### Hyperparameter Tuning
```python
from automl import TuningIntegrator

# Create tuning integrator
tuner = TuningIntegrator(automl)

# Advanced model tuning
summary = tuner.tune_models(
    X_train, y_train,
    search_type='bayesian',  # 'grid', 'random', 'bayesian'
    n_iter=50,               # Number of iterations
    register_best=True       # Automatically register best models
)
```

### Custom Model Registration
```python
from sklearn.ensemble import ExtraTreesClassifier

# Register a custom model
custom_model = ExtraTreesClassifier(n_estimators=200)
automl.register_model(
    'MyCustomModel',
    custom_model,
    preprocessor=custom_preprocessor  # Optional
)
```

### Feature Importance
```python
# Get feature importance
importance = automl.get_feature_importance()
print("Top Features:", importance)
```

### Model Persistence
```python
# Save the best model
automl.save_best_model('best_model.pkl')

# Load a saved model
loaded_model = automl.load_model('best_model.pkl')
```

## Best Practices

### Data Preparation
- Clean and preprocess your data
- Handle missing values
- Normalize or scale features
- Use train-test split

### Model Selection
- Try multiple problem types
- Compare different models
- Consider ensemble methods

### Overfitting Prevention
- Use cross-validation
- Monitor performance metrics
- Apply regularization
- Collect more training data if possible

### Performance Optimization
- Increase `n_iter` for more thorough searches
- Use appropriate problem type
- Monitor computational resources

## Troubleshooting

### Common Issues
1. **Incompatible Data**
   - Ensure correct data shape
   - Check data types
   - Verify feature scaling

2. **Poor Performance**
   - Increase training data
   - Try different models
   - Perform feature engineering

3. **Memory Constraints**
   - Reduce model complexity
   - Use subset of data
   - Increase computational resources

### Debugging Tips
- Use `verbose` parameter for detailed logs
- Check data quality before training
- Validate input data types

### Getting Help
- Consult [documentation](README.md)
- Open GitHub issues
- Check error messages carefully

## Advanced Configuration

### Custom Configuration
```python
automl = AutoML({
    'problem_type': 'classification',
    'random_state': 42,
    'custom_models': {
        'MyModel': custom_model_instance
    }
})
```

## Performance Monitoring

### Detailed Evaluation
```python
# Get comprehensive training logs
logs = automl.get_all_training_logs()

# Detailed fit evaluation
fit_eval = automl.get_fit_evaluation()
print(fit_eval['fit_quality'])
```

---

<div align="center">
🚀 **Empower Your Machine Learning Journey** 🤖

*Simplifying Complex Machine Learning Workflows*
</div>
