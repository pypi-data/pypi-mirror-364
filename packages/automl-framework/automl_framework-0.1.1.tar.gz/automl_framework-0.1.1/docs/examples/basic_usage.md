# Basic Usage of AutoML Framework

## 🚀 Getting Started with AutoML

### Classification Example
```python
from automl import AutoML
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load Iris dataset
X, y = load_iris(return_X_y=True)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize AutoML for classification
automl = AutoML(problem_type='classification')

# Train models
automl.fit(X_train, y_train)

# Evaluate models
results = automl.evaluate(X_test, y_test)

# Get best model predictions
predictions = automl.predict(X_test)

# View performance leaderboard
leaderboard = automl.get_leaderboard()
print(leaderboard)
```

### Regression Example
```python
from automl import AutoML
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

# Load Boston Housing dataset
X, y = load_boston(return_X_y=True)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize AutoML for regression
automl = AutoML(problem_type='regression')

# Train models
automl.fit(X_train, y_train)

# Evaluate models
results = automl.evaluate(X_test, y_test)

# Get best model predictions
predictions = automl.predict(X_test)

# View performance insights
print(automl.get_leaderboard())
```

## 🔍 Key Features Demonstrated

### Model Training
- Automatic model selection
- Multiple algorithm support
- Easy training interface

### Evaluation
- Comprehensive performance metrics
- Model comparison leaderboard
- Detailed performance insights

### Prediction
- Simple prediction method
- Works with best-performing model

## 💡 Additional Tips
- Use `problem_type` to specify task
- Split data before training
- Evaluate models on test set
- Explore leaderboard for insights

## 🚀 Next Steps
- Try different datasets
- Experiment with preprocessing
- Explore advanced features
- Customize model selection

---

<div align="center">
🤖 **Automate Your Machine Learning** 🚀

*Simple, powerful, intelligent*
</div>
