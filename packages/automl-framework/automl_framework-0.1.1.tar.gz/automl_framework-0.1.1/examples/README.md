# AutoML Framework Examples

This directory contains comprehensive examples demonstrating the capabilities of the AutoML Framework. Each example is designed to showcase different aspects of the framework, from basic usage to advanced features.

## 📁 Example Files

### 🚀 **Quick Start Examples**

#### [`basic_usage.py`](basic_usage.py)
**Perfect for beginners!** Demonstrates fundamental AutoML operations:
- Loading and preparing data
- Training multiple models automatically
- Evaluating model performance
- Making predictions
- Basic overfitting detection

```bash
python basic_usage.py
```

#### [`run_automl.py`](run_automl.py)
**One-line AutoML solution!** The simplest way to get results:
- Complete AutoML pipeline in a single function call
- Automatic problem type detection
- Built-in overfitting handling
- Visualization and reporting
- Production-ready model output

```bash
python run_automl.py
```

### 🧠 **Advanced Examples**

#### [`advanced_example.py`](advanced_example.py)
**For power users!** Showcases advanced features:
- Custom model registration and configuration
- Advanced overfitting detection and mitigation
- Hyperparameter tuning with multiple strategies
- Model comparison and analysis
- Feature engineering and selection
- Production deployment preparation

```bash
python advanced_example.py
```

#### [`overfitting_demo.py`](overfitting_demo.py) *(Coming Soon)*
**Overfitting detection deep dive:**
- Creating datasets prone to overfitting
- Demonstrating overfitting detection algorithms
- Comparing mitigation strategies
- Visualizing overfitting patterns

#### [`hyperparameter_tuning.py`](hyperparameter_tuning.py) *(Coming Soon)*
**Hyperparameter optimization showcase:**
- Grid, Random, and Bayesian search
- Custom parameter grids
- Performance comparison plots
- Integration with AutoML pipeline

## 🎯 **Usage Scenarios**

### **Scenario 1: Quick Prototyping**
Use `run_automl.py` when you need fast results:
```python
from examples.run_automl import run_automl
import pandas as pd

df = pd.read_csv('your_data.csv')
results = run_automl(df, target_column='target', problem_type='auto')
print(f"Best model: {results['best_model_name']}")
```

### **Scenario 2: Learning the Framework**
Start with `basic_usage.py` to understand core concepts:
```python
python basic_usage.py
```

### **Scenario 3: Production Implementation**
Use `advanced_example.py` for production-ready code:
```python
python advanced_example.py
```

## 📊 **Example Datasets**

The examples use various datasets to demonstrate different scenarios:

- **Synthetic Data**: Generated datasets for consistent results
- **Iris Dataset**: Classic classification problem (3 classes, 4 features)
- **Wine Dataset**: Multi-class classification (3 classes, 13 features)
- **Boston Housing**: Regression problem (1 target, 13 features)
- **Breast Cancer**: Binary classification (2 classes, 30 features)

## 🔧 **Running Examples**

### **Prerequisites**
```bash
# Install the AutoML Framework
pip install automl-framework

# Or install from source with examples dependencies
pip install -e .[examples]
```

### **Running Individual Examples**
```bash
# From the project root directory
cd examples/

# Run basic usage example
python basic_usage.py

# Run one-line AutoML
python run_automl.py

# Run advanced features
python advanced_example.py
```

### **Interactive Usage**
```python
# In Python interpreter or Jupyter notebook
import sys
sys.path.append('../')  # If running from examples directory

# Import and run example functions
from examples.basic_usage import example_with_synthetic_data
automl = example_with_synthetic_data()

# Use the trained AutoML object
predictions = automl.predict(your_test_data)
```

## 🎨 **Customizing Examples**

### **Using Your Own Data**
Replace the dataset loading section in any example:
```python
# Instead of synthetic data
# X, y = make_classification(...)

# Use your data
df = pd.read_csv('your_data.csv')
X = df.drop('target_column', axis=1)
y = df['target_column']
```

### **Adding Custom Models**
Extend examples with your own models:
```python
from sklearn.ensemble import ExtraTreesClassifier

# Add to any example
automl.register_model('ExtraTrees', ExtraTreesClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42
))
```

### **Custom Preprocessing**
Add your own preprocessing steps:
```python
from automl.preprocessors import Preprocessor

class CustomPreprocessor(Preprocessor):
    def fit(self, X, y=None):
        # Your preprocessing logic
        return self

    def transform(self, X):
        # Your transformation logic
        return X

automl.register_model('CustomModel', your_model, CustomPreprocessor())
```

## 📈 **Expected Outputs**

### **Basic Usage Example**
```
Starting AutoML demonstration
Loading data from iris dataset
Checking data quality...
Training models...
Successfully trained RandomForest in 0.45 seconds
Successfully trained LogisticRegression in 0.12 seconds
...
Model Leaderboard:
                model  test_accuracy  test_f1  fit_quality
0        RandomForest         0.9667   0.9667    Good fit
1  LogisticRegression         0.9333   0.9333    Good fit
...
Best model: RandomForest with test_accuracy: 0.9667
```

### **Advanced Example**
```
=== Advanced AutoML Features Demo ===
Custom model registered: GradientBoosting
Custom model registered: ExtraTrees
Enabling overfitting detection...
Training 8 models...
Overfitting detected in DecisionTree: Score=0.45, Severity=Moderate
Applying regularization mitigation...
Hyperparameter tuning with Bayesian optimization...
Best tuned model: RandomForest_tuned with accuracy: 0.9733
Feature importance analysis completed
Production deployment package saved to: models/
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```python
# Error: ModuleNotFoundError: No module named 'automl'
# Solution: Install the package or add to Python path
pip install -e .  # If running from source
# or
import sys; sys.path.append('../')
```

#### **Missing Dependencies**
```python
# Error: No module named 'scikit-optimize'
# Solution: Install optional dependencies
pip install automl-framework[all]  # All optional dependencies
# or
pip install scikit-optimize hyperopt  # Specific dependencies
```

#### **Data Loading Issues**
```python
# Error: File not found
# Solution: Use absolute paths or check working directory
import os
print(f"Current directory: {os.getcwd()}")
# Use full path to data files
```

### **Performance Notes**
- Examples are designed for demonstration, not performance
- Increase `n_estimators`, `n_iter` for better results in production
- Use `n_jobs=-1` for parallel processing on multi-core systems
- Consider using `random_state` for reproducible results

## 📚 **Learning Path**

We recommend following this learning path:

1. **Start Here**: [`basic_usage.py`](basic_usage.py)
   - Understand core AutoML concepts
   - Learn basic workflow

2. **Quick Results**: [`run_automl.py`](run_automl.py)
   - See the full power in one function
   - Understand automatic features

3. **Go Deeper**: [`advanced_example.py`](advanced_example.py)
   - Learn customization options
   - Understand advanced features

4. **Specialize**: Domain-specific examples
   - Choose examples relevant to your use case
   - Adapt patterns to your data

## 🤝 **Contributing Examples**

We welcome new examples! To contribute:

1. **Follow the pattern**: Use existing examples as templates
2. **Document well**: Include clear comments and docstrings
3. **Test thoroughly**: Ensure examples run without errors
4. **Add to README**: Update this file with your example description

### **Example Template**
```python
"""
[Example Name] - [Brief Description]

This example demonstrates [specific feature/use case].

Usage:
    python your_example.py

Requirements:
    - List any special requirements
    - Specific datasets needed
    - Optional dependencies
"""

def main():
    """Main example function with clear steps"""
    print("=== [Example Name] ===")

    # Step 1: Data preparation
    # Step 2: AutoML setup
    # Step 3: Training
    # Step 4: Evaluation
    # Step 5: Results analysis

    print("Example completed successfully!")

if __name__ == "__main__":
    main()
```

## 📞 **Need Help?**

- 📖 **Documentation**: Check the main [README](../README.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/nandarizkika/automl-framework/discussions)
- 🐛 **Issues**: [Report bugs](https://github.com/nandarizkika/automl-framework/issues)
- 📧 **Email**: nandarizky52@gmail.com

---

**Happy learning! 🚀**
