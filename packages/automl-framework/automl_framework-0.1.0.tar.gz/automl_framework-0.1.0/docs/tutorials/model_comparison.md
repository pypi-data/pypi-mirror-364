# Model Comparison and Evaluation Tutorial

## 🌟 Comprehensive Model Performance Analysis

This tutorial explores advanced techniques for comparing, evaluating, and understanding machine learning models using the AutoML Framework.

## 📋 Prerequisites
- Basic machine learning knowledge
- Completed Getting Started Tutorial
- AutoML Framework installed
  ```bash
  pip install automl-framework[all]
  ```

## 🧠 Tutorial Objectives
- Compare multiple models
- Understand performance metrics
- Visualize model comparisons
- Make informed model selection decisions

## 1. 🚀 Comprehensive Model Comparison

### Detailed Model Evaluation Workflow
```python
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from automl import AutoML
from sklearn.model_selection import train_test_split

# Load breast cancer dataset
X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize AutoML
automl = AutoML(problem_type='classification')

# Train multiple models
automl.fit(X_train, y_train)

# Comprehensive evaluation
results = automl.evaluate(X_test, y_test)

# Get performance leaderboard
leaderboard = automl.get_leaderboard()
print("Model Performance Leaderboard:")
print(leaderboard)
```

## 2. 🔬 Performance Metrics Deep Dive

### Understanding Evaluation Metrics
```python
def detailed_metrics_analysis(automl, X_test, y_test):
    """
    Provide comprehensive model performance analysis

    Args:
        automl: Trained AutoML instance
        X_test: Test features
        y_test: Test labels

    Returns:
        Detailed performance insights
    """
    # Get leaderboard
    leaderboard = automl.get_leaderboard()

    # Detailed metrics analysis
    print("🏆 Comprehensive Model Performance Analysis 🏆")

    for _, row in leaderboard.iterrows():
        model_name = row['model']

        print(f"\n📊 Model: {model_name}")
        print("-" * 40)

        # Performance metrics
        print(f"Accuracy: {row.get('test_accuracy', 'N/A'):.4f}")
        print(f"Precision: {row.get('test_precision', 'N/A'):.4f}")
        print(f"Recall: {row.get('test_recall', 'N/A'):.4f}")
        print(f"F1 Score: {row.get('test_f1', 'N/A'):.4f}")

        # Overfitting assessment
        print(f"\n🔍 Overfitting Assessment:")
        print(f"Fit Quality: {row.get('fit_quality', 'N/A')}")
        print(f"Overfitting Score: {row.get('overfitting_score', 'N/A'):.4f}")

        # Performance consistency
        print(f"\n📈 Performance Consistency:")
        print(f"Accuracy Gap: {row.get('accuracy_gap', 'N/A'):.4f}")
        print(f"Precision Gap: {row.get('precision_gap', 'N/A'):.4f}")
        print(f"Recall Gap: {row.get('recall_gap', 'N/A'):.4f}")

# Run detailed analysis
detailed_metrics_analysis(automl, X_test, y_test)
```

## 3. 🖼️ Model Comparison Visualization

### Advanced Visualization Techniques
```python
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_model_comparison(leaderboard):
    """
    Create comprehensive model comparison visualizations

    Args:
        leaderboard: DataFrame with model performance metrics
    """
    plt.figure(figsize=(15, 10))

    # Subplot 1: Performance Metrics Comparison
    plt.subplot(2, 2, 1)
    metrics_to_plot = ['test_accuracy', 'test_precision', 'test_recall', 'test_f1']
    leaderboard[metrics_to_plot].plot(kind='bar', ax=plt.gca())
    plt.title('Performance Metrics Comparison')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Subplot 2: Overfitting Assessment
    plt.subplot(2, 2, 2)
    sns.scatterplot(
        data=leaderboard,
        x='test_accuracy',
        y='overfitting_score',
        hue='model'
    )
    plt.title('Accuracy vs Overfitting')

    # Subplot 3: Performance Gaps
    plt.subplot(2, 2, 3)
    gap_metrics = ['accuracy_gap', 'precision_gap', 'recall_gap']
    leaderboard[gap_metrics].plot(kind='bar', ax=plt.gca())
    plt.title('Performance Consistency Gaps')
    plt.xticks(rotation=45, ha='right')

    # Subplot 4: Training Time Comparison
    plt.subplot(2, 2, 4)
    leaderboard['training_time'].plot(kind='bar', ax=plt.gca())
    plt.title('Model Training Time')
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

# Visualize model comparison
visualize_model_comparison(leaderboard)
```

## 4. 🧩 Advanced Model Selection

### Intelligent Model Selection Strategy
```python
def intelligent_model_selection(leaderboard, problem_constraints):
    """
    Select the most appropriate model based on constraints

    Args:
        leaderboard: DataFrame with model performance
        problem_constraints: Dict with selection criteria

    Returns:
        Best model based on constraints
    """
    # Define selection criteria
    criteria = {
        'performance_threshold': problem_constraints.get('min_accuracy', 0.9),
        'complexity_limit': problem_constraints.get('max_complexity', 'medium'),
        'training_time_limit': problem_constraints.get('max_training_time', 10)
    }

    # Filter models meeting basic performance criteria
    filtered_models = leaderboard[
        (leaderboard['test_accuracy'] >= criteria['performance_threshold']) &
        (leaderboard['overfitting_score'] <= 0.2)
    ]

# Complexity mapping
    complexity_map = {
        'low': ['LogisticRegression', 'LinearModel'],
        'medium': ['RandomForest', 'GradientBoosting'],
        'high': ['DeepNeuralNetwork', 'ComplexEnsemble']
    }

    # Additional filtering based on complexity
    if criteria['complexity_limit']:
        allowed_models = complexity_map.get(criteria['complexity_limit'], [])
        filtered_models = filtered_models[
            filtered_models['model'].isin(allowed_models)
        ]

    # Filter by training time
    filtered_models = filtered_models[
        filtered_models['training_time'] <= criteria['training_time_limit']
    ]

    # Ranking criteria
    if not filtered_models.empty:
        # Multi-objective ranking
        filtered_models['rank_score'] = (
            filtered_models['test_accuracy'] * 0.4 +
            (1 - filtered_models['overfitting_score']) * 0.3 +
            (1 / filtered_models['training_time']) * 0.3
        )

        # Select top model
        best_model = filtered_models.sort_values('rank_score', ascending=False).iloc[0]

        print("🏆 Recommended Model:")
        print(f"Model Name: {best_model['model']}")
        print(f"Accuracy: {best_model['test_accuracy']:.4f}")
        print(f"Overfitting Score: {best_model['overfitting_score']:.4f}")
        print(f"Training Time: {best_model['training_time']:.2f} seconds")

        return best_model
    else:
        print("❌ No models meet the specified constraints")
        return None

# Example usage
problem_constraints = {
    'min_accuracy': 0.90,
    'max_complexity': 'medium',
    'max_training_time': 5  # seconds
}

best_model = intelligent_model_selection(leaderboard, problem_constraints)
```

## 5. 🔍 Feature Importance Comparison

### Comparing Feature Contributions
```python
def compare_feature_importance(automl):
    """
    Visualize and compare feature importance across models

    Args:
        automl: Trained AutoML instance
    """
    # Get feature importances for all models
    feature_importances = {}

    for model_name in automl.results.keys():
        try:
            importance = automl.get_feature_importance(model_name)
            feature_importances[model_name] = importance
        except Exception as e:
            print(f"Could not get feature importance for {model_name}: {e}")

    # Visualization
    plt.figure(figsize=(15, 10))

    # Prepare data for plotting
    importance_df = pd.DataFrame(feature_importances)

    # Heatmap of feature importances
    plt.subplot(2, 1, 1)
    sns.heatmap(
        importance_df,
        cmap='viridis',
        annot=True,
        fmt='.3f',
        cbar_kws={'label': 'Feature Importance'}
    )
    plt.title('Feature Importance Across Models')
    plt.xlabel('Models')
    plt.ylabel('Features')

    # Boxplot of feature importance distribution
    plt.subplot(2, 1, 2)
    importance_df.plot(kind='box', ax=plt.gca())
    plt.title('Distribution of Feature Importances')
    plt.xlabel('Models')
    plt.ylabel('Importance Score')

    plt.tight_layout()
    plt.show()

# Compare feature importances
compare_feature_importance(automl)
```

## 6. 🧪 Cross-Validation Performance

### Robust Performance Estimation
```python
def cross_validation_performance_analysis(automl, X, y):
    """
    Perform comprehensive cross-validation analysis

    Args:
        automl: AutoML instance
        X: Feature matrix
        y: Target variable

    Returns:
        Detailed cross-validation results
    """
    from sklearn.model_selection import cross_validate

    cv_results = {}

    for model_name, model_wrapper in automl.registry.get_models().items():
        try:
            # Perform cross-validation
            cv_scores = cross_validate(
                model_wrapper.model,
                X, y,
                cv=5,  # 5-fold cross-validation
                scoring=['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'],
                return_train_score=True
            )

            # Prepare results
            cv_results[model_name] = {
                'test_scores': {
                    'accuracy': cv_scores['test_accuracy'].mean(),
                    'precision': cv_scores['test_precision_weighted'].mean(),
                    'recall': cv_scores['test_recall_weighted'].mean(),
                    'f1_score': cv_scores['test_f1_weighted'].mean()
                },
                'train_scores': {
                    'accuracy': cv_scores['train_accuracy'].mean(),
                    'precision': cv_scores['train_precision_weighted'].mean(),
                    'recall': cv_scores['train_recall_weighted'].mean(),
                    'f1_score': cv_scores['train_f1_weighted'].mean()
                },
                'score_variability': {
                    'accuracy_std': cv_scores['test_accuracy'].std(),
                    'precision_std': cv_scores['test_precision_weighted'].std(),
                    'recall_std': cv_scores['test_recall_weighted'].std(),
                    'f1_score_std': cv_scores['test_f1_weighted'].std()
                }
            }
        except Exception as e:
            print(f"Cross-validation failed for {model_name}: {e}")

    # Visualization
    plt.figure(figsize=(15, 10))

    # Prepare data for plotting
    cv_df = pd.DataFrame.from_dict(
        {model: data['test_scores'] for model, data in cv_results.items()},
        orient='index'
    )

    # Bar plot of cross-validation scores
    cv_df.plot(kind='bar', ax=plt.gca())
    plt.title('Cross-Validation Performance Comparison')
    plt.xlabel('Models')
    plt.ylabel('Score')
    plt.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

    return cv_results

# Perform cross-validation analysis
cv_analysis = cross_validation_performance_analysis(automl, X, y)
```

## 🎓 Learning Objectives
- ✅ Compare model performances comprehensively
- ✅ Visualize model metrics
- ✅ Understand feature importance
- ✅ Perform robust cross-validation
- ✅ Make informed model selection decisions

## 🚀 Best Practices
1. Never rely on a single metric
2. Consider model complexity
3. Analyze feature contributions
4. Use cross-validation
5. Understand your problem's specific requirements

## 💡 Advanced Challenges
- Develop custom model ranking algorithms
- Create domain-specific model selection criteria
- Implement ensemble model selection
- Build adaptive model selection strategies

## 🔍 Recommended Next Steps
- Experiment with different datasets
- Try various problem types
- Develop custom comparison metrics
- Share your model comparison insights

---

<div align="center">
🌟 **Master the Art of Model Comparison** 🧠

*Choosing the right model is a science and an art*
</div>
