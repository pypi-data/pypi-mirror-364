"""
Basic usage example for AutoML Framework
"""

import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, load_wine
from sklearn.ensemble import AdaBoostClassifier

from automl import AutoML
from automl.utils import DataUtils, setup_logging


def example_with_synthetic_data():
    """Example using synthetic classification data"""
    print("=== Basic AutoML Example with Synthetic Data ===")

    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        n_classes=2,
        random_state=42,
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X = pd.DataFrame(X, columns=feature_names)
    y = pd.Series(y, name="target")

    print(f"Dataset shape: {X.shape}")
    print(f"Target distribution:\n{y.value_counts(normalize=True)}")

    data_report = DataUtils.check_data_quality(X, y)
    print("\nData quality report:")
    for key, value in data_report.items():
        print(f"- {key}: {value}")

    X_train, X_test, y_train, y_test = DataUtils.train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    config = {"problem_type": "classification", "random_state": 42}
    automl = AutoML(config)

    automl.register_model(
        "AdaBoost", AdaBoostClassifier(n_estimators=50, random_state=42)
    )

    print("\nTraining models...")
    automl.fit(X_train, y_train)

    print("Evaluating models...")
    results = automl.evaluate(X_test, y_test)

    print("\nModel Leaderboard:")
    leaderboard = automl.get_leaderboard()
    print(leaderboard)

    print(f"\nBest model: {automl.pipeline.best_model_name}")

    predictions = automl.predict(X_test)

    from sklearn.metrics import accuracy_score, classification_report

    accuracy = accuracy_score(y_test, predictions)
    print(f"Test accuracy: {accuracy:.4f}")

    importance = automl.get_feature_importance()
    if importance:
        print("\nTop 5 most important features:")
        if "feature_importances_" in importance:
            imp_scores = importance["feature_importances_"]
            feature_imp = pd.DataFrame(
                {"feature": feature_names, "importance": imp_scores}
            ).sort_values("importance", ascending=False)
            print(feature_imp.head())

    summary = automl.get_training_summary()
    print("\nTraining Summary:")
    print(f"- Models trained: {summary['n_models_trained']}")
    print(f"- Successful: {len(summary['successful_models'])}")
    print(f"- Failed: {len(summary['failed_models'])}")

    return automl


def example_with_wine_dataset():
    """Example using the wine dataset"""
    print("\n\n=== AutoML Example with Wine Dataset ===")

    wine = load_wine()
    X = pd.DataFrame(wine.data, columns=wine.feature_names)
    y = pd.Series(wine.target, name="wine_class")

    print(f"Dataset shape: {X.shape}")
    print(f"Number of classes: {len(np.unique(y))}")
    print(f"Class distribution:\n{y.value_counts()}")

    X_train, X_test, y_train, y_test = DataUtils.train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    automl = AutoML({"problem_type": "classification", "random_state": 42})

    print("\nTraining models...")
    automl.fit(X_train, y_train)

    print("Evaluating models...")
    automl.evaluate(X_test, y_test)

    print("\nLeaderboard:")
    leaderboard = automl.get_leaderboard()
    print(leaderboard[["model", "test_accuracy", "test_f1", "fit_quality"]])

    predictions = automl.predict(X_test)

    from sklearn.metrics import classification_report

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, predictions, target_names=wine.target_names))

    return automl


def example_with_overfitting_analysis():
    """Example demonstrating overfitting detection"""
    print("\n\n=== Overfitting Detection Example ===")

    X, y = make_classification(
        n_samples=100,
        n_features=50,
        n_informative=10,
        n_redundant=10,
        n_classes=2,
        random_state=42,
    )

    X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
    y = pd.Series(y)

    X_train, X_test, y_train, y_test = DataUtils.train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    automl = AutoML({"problem_type": "classification", "random_state": 42})

    if hasattr(automl.pipeline, "set_overfitting_control"):
        automl.pipeline.set_overfitting_control(
            detection_enabled=True, auto_mitigation=True, threshold=0.2
        )
        print("Overfitting detection enabled")

    automl.fit(X_train, y_train)
    automl.evaluate(X_test, y_test)

    print("\nOverfitting Analysis:")
    try:
        fit_evaluations = automl.get_all_fit_evaluations()
        for model_name, eval_data in fit_evaluations.items():
            fit_quality = eval_data.get("fit_quality", "Unknown")
            overfitting_score = eval_data.get("overfitting_score", 0)

            print(f"\n{model_name}:")
            print(f"  Fit Quality: {fit_quality}")
            print(f"  Overfitting Score: {overfitting_score:.4f}")

            suggestions = automl.get_improvement_suggestions(model_name)
            if suggestions:
                print("  Suggestions:")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"    {i}. {suggestion}")
    except Exception as e:
        print(f"Could not analyze overfitting: {e}")

    return automl


if __name__ == "__main__":
    logger = setup_logging(level="INFO")

    try:
        automl1 = example_with_synthetic_data()
    except Exception as e:
        print(f"Error in synthetic data example: {e}")

    try:
        automl2 = example_with_wine_dataset()
    except Exception as e:
        print(f"Error in wine dataset example: {e}")

    try:
        automl3 = example_with_overfitting_analysis()
    except Exception as e:
        print(f"Error in overfitting analysis example: {e}")

    print("\n=== All examples completed ===")
