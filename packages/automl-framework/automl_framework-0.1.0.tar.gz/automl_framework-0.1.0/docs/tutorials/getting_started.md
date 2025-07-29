# Getting Started with AutoML Framework

## 🚀 Introduction

Welcome to the AutoML Framework tutorial! This guide will walk you through your first machine learning project using our powerful, automated library.

## 📋 Prerequisites
- Python 3.8+
- Basic understanding of machine learning concepts
- Installed AutoML Framework
  ```bash
  pip install automl-framework
  ```

## 🧠 Tutorial Outline
1. Data Preparation
2. Model Training
3. Evaluation
4. Prediction
5. Advanced Insights

## 🔍 Step 1: Importing Libraries and Preparing Data

```python
# Import required libraries
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load sample dataset
X, y = load_iris(return_X_y=True)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,  # 20% for testing
    random_state=42  # Reproducibility
)

# Print dataset information
print("Training data shape:", X_train.shape)
print("Testing data shape:", X_test.shape)
```

## 🤖 Step 2: Initialize AutoML

```python
from automl import AutoML

# Create AutoML instance for classification
automl = AutoML(
    problem_type='classification',
    random_state=42
)
```

## 🏋️ Step 3: Train Models

```python
# Fit models to the training data
automl.fit(X_train, y_train)
```

## 📊 Step 4: Model Evaluation

```python
# Evaluate models on test data
results = automl.evaluate(X_test, y_test)

# Get performance leaderboard
leaderboard = automl.get_leaderboard()
print("Model Performance Leaderboard:")
print(leaderboard)
```

## 🎯 Step 5: Make Predictions

```python
# Predict using the best model
predictions = automl.predict(X_test)

# Get prediction probabilities
probabilities = automl.predict_proba(X_test)
```

## 🔬 Step 6: Deep Dive into Results

```python
# Get feature importance
feature_importance = automl.get_feature_importance()
print("\nFeature Importance:")
for feature, importance in feature_importance.items():
    print(f"{feature}: {importance}")

# Get overfitting assessment
assessment = automl.get_overfitting_assessment()
print("\nOverfitting Assessment:")
print("Severity:", assessment['severity'])
```

## 💡 Advanced Insights

### Overfitting Control
```python
# Configure overfitting detection
automl.pipeline.set_overfitting_control(
    detection_enabled=True,    # Enable detection
    auto_mitigation=True,      # Automatically mitigate
    threshold=0.3              # Sensitivity level
)
```

### Model Persistence
```python
# Save the best model
automl.save_best_model('iris_model.pkl')

# Load the model later
loaded_model = automl.load_model('iris_model.pkl')
```

## 🎓 Learning Objectives Achieved
- ✅ Loaded and prepared dataset
- ✅ Trained multiple machine learning models
- ✅ Evaluated model performance
- ✅ Made predictions
- ✅ Analyzed feature importance
- ✅ Detected potential overfitting

## 🚀 Next Steps
- Explore advanced features
- Try different datasets
- Experiment with custom preprocessors
- Join our community discussions

## 💬 Troubleshooting Tips
- Ensure all dependencies are installed
- Check data types and shapes
- Use `print()` statements to debug
- Consult our documentation for detailed guidance

---

<div align="center">
🌟 **Congratulations on Your First AutoML Project!** 🎉

*Every machine learning journey begins with a single model*
</div>
