"""
Advanced AutoML Framework Example

This example demonstrates the advanced features of the AutoML Framework including:
- Custom model registration and configuration
- Advanced overfitting detection and mitigation
- Hyperparameter tuning with multiple strategies
- Comprehensive model analysis and comparison
- Feature engineering and selection
- Production deployment preparation

Usage:
    python advanced_example.py

Requirements:
    - automl-framework
    - scikit-learn
    - pandas
    - numpy
    - matplotlib
    - seaborn

Optional (for advanced features):
    - scikit-optimize (for Bayesian optimization)
    - hyperopt (for advanced hyperparameter tuning)
"""

from automl import AutoML
from automl.utils import DataUtils, setup_logging
from automl.preprocessors import Preprocessor, StandardPreprocessor

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from sklearn.datasets import make_classification, load_breast_cancer, load_wine
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix

sys.path.append("../")

try:
    from automl.automl_integration import TuningIntegrator

    TUNING_AVAILABLE = True
except ImportError:
    TUNING_AVAILABLE = False
    warnings.warn(
        "TuningIntegrator not available. Hyperparameter tuning examples will be skipped."
    )


class AdvancedPreprocessor(Preprocessor):
    """
    Custom preprocessor with feature selection and scaling
    """

    def __init__(self, feature_selection=True, n_features=None):
        self.feature_selection = feature_selection
        self.n_features = n_features
        self.scaler = None
        self.selector = None

    def fit(self, X, y=None):
        """Fit the preprocessor to training data"""
        from sklearn.preprocessing import StandardScaler
        from sklearn.feature_selection import SelectKBest, f_classif

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        if self.feature_selection and y is not None:
            n_features = self.n_features or min(10, X.shape[1])
            self.selector = SelectKBest(score_func=f_classif, k=n_features)
            self.selector.fit(X_scaled, y)

        return self

    def transform(self, X):
        """Transform new data"""
        if self.scaler is None:
            raise ValueError("Preprocessor not fitted")

        X_scaled = self.scaler.transform(X)

        if self.selector is not None:
            X_scaled = self.selector.transform(X_scaled)

        return X_scaled


def create_challenging_dataset():
    """
    Create a dataset that's prone to overfitting for demonstration
    """
    print("Creating challenging dataset prone to overfitting...")

    X, y = make_classification(
        n_samples=200,
        n_features=50,
        n_informative=15,
        n_redundant=10,
        n_clusters_per_class=1,
        class_sep=0.8,
        random_state=42,
    )

    feature_names = [f"feature_{i:02d}" for i in range(X.shape[1])]
    X = pd.DataFrame(X, columns=feature_names)
    y = pd.Series(y, name="target")

    print(f"Dataset created: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"Class distribution: {y.value_counts().to_dict()}")

    return X, y


def advanced_model_registration_demo():
    """
    Demonstrate advanced model registration with custom preprocessing
    """
    print("\n" + "=" * 60)
    print("ADVANCED MODEL REGISTRATION DEMO")
    print("=" * 60)

    config = {"problem_type": "classification", "random_state": 42}
    automl = AutoML(config)

    print("\nRegistering advanced models...")

    automl.register_model(
        "ExtraTrees_Custom",
        ExtraTreesClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features="sqrt",
            bootstrap=False,
            random_state=42,
        ),
        AdvancedPreprocessor(feature_selection=True, n_features=15),
    )

    automl.register_model(
        "GradientBoosting_Regularized",
        GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42,
        ),
    )

    automl.register_model(
        "SVM_RBF",
        SVC(C=1.0, kernel="rbf", gamma="scale", probability=True, random_state=42),
        StandardPreprocessor(),
    )

    automl.register_model(
        "MLP_Custom",
        MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation="relu",
            solver="adam",
            alpha=0.01,
            learning_rate="adaptive",
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.2,
            random_state=42,
        ),
        StandardPreprocessor(),
    )

    print(f"Registered {len(automl.pipeline.registry.get_models())} models")

    print("\nModel Reference Information:")
    model_ref = automl.get_model_reference()
    for model_name, info in model_ref.items():
        print(f"\n{model_name}:")
        print(f"  Description: {info.get('description', 'Custom model')}")
        if "strengths" in info:
            print(f"  Strengths: {info['strengths']}")
        if "overfitting_risk" in info:
            print(f"  Overfitting Risk: {info['overfitting_risk']}")

    return automl


def overfitting_detection_demo(automl, X, y):
    """
    Demonstrate advanced overfitting detection and mitigation
    """
    print("\n" + "=" * 60)
    print("OVERFITTING DETECTION & MITIGATION DEMO")
    print("=" * 60)

    X_train, X_test, y_train, y_test = DataUtils.train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")

    if hasattr(automl.pipeline, "set_overfitting_control"):
        print("\nConfiguring overfitting detection...")
        automl.pipeline.set_overfitting_control(
            detection_enabled=True, auto_mitigation=True, threshold=0.2
        )
        print("✓ Overfitting detection enabled")
        print("✓ Automatic mitigation enabled")
        print("✓ Mitigation threshold: 0.2")

    print("\nTraining models with overfitting monitoring...")
    start_time = datetime.now()
    automl.fit(X_train, y_train)
    training_time = (datetime.now() - start_time).total_seconds()

    print("Evaluating models...")
    start_time = datetime.now()
    automl.evaluate(X_test, y_test)
    evaluation_time = (datetime.now() - start_time).total_seconds()

    print(f"Training completed in {training_time:.2f} seconds")
    print(f"Evaluation completed in {evaluation_time:.2f} seconds")

    summary = automl.get_training_summary()
    print("\nTraining Summary:")
    print(f"  Models trained: {summary['n_models_trained']}")
    print(f"  Successful models: {len(summary['successful_models'])}")
    print(f"  Failed models: {len(summary['failed_models'])}")

    if hasattr(automl.pipeline, "get_mitigated_models"):
        mitigated = automl.pipeline.get_mitigated_models()
        if mitigated:
            print(f"  Models with overfitting mitigation: {len(mitigated)}")
            for name, info in mitigated.items():
                print(f"    - {name}: {info['strategy']}")

    print("\n" + "-" * 50)
    print("DETAILED OVERFITTING ANALYSIS")
    print("-" * 50)

    try:
        fit_evaluations = automl.get_all_fit_evaluations()
        overfitting_detected = []

        for model_name, eval_data in fit_evaluations.items():
            fit_quality = eval_data.get("fit_quality", "Unknown")
            overfitting_score = eval_data.get("overfitting_score", 0)
            underfitting_score = eval_data.get("underfitting_score", 0)

            print(f"\n{model_name}:")
            print(f"  Fit Quality: {fit_quality}")
            print(f"  Overfitting Score: {overfitting_score:.4f}")
            print(f"  Underfitting Score: {underfitting_score:.4f}")

            if overfitting_score > 0.2:
                overfitting_detected.append(model_name)
                print("  ⚠️  Overfitting detected!")

                suggestions = automl.get_improvement_suggestions(model_name)
                if suggestions:
                    print("  Improvement Suggestions:")
                    for i, suggestion in enumerate(suggestions[:3], 1):
                        print(f"    {i}. {suggestion}")

                if hasattr(automl.pipeline, "get_overfitting_assessment"):
                    assessment = automl.pipeline.get_overfitting_assessment(model_name)
                    severity = assessment.get("severity", "Unknown")
                    print(f"  Severity: {severity}")

        print(
            f"\nSummary: {len(overfitting_detected)} out of {len(fit_evaluations)} models show overfitting"
        )

    except Exception as e:
        print(f"Error in overfitting analysis: {e}")

    return X_train, X_test, y_train, y_test


def hyperparameter_tuning_demo(automl, X_train, y_train):
    """
    Demonstrate advanced hyperparameter tuning
    """
    if not TUNING_AVAILABLE:
        print("\n" + "=" * 60)
        print("HYPERPARAMETER TUNING DEMO (SKIPPED)")
        print("=" * 60)
        print("TuningIntegrator not available. Install with:")
        print("pip install scikit-optimize hyperopt")
        return

    print("\n" + "=" * 60)
    print("HYPERPARAMETER TUNING DEMO")
    print("=" * 60)

    tuner = TuningIntegrator(automl, output_dir="tuning_results")

    models_to_tune = [
        "RandomForest",
        "GradientBoosting_Regularized",
        "ExtraTrees_Custom",
    ]

    print(f"Tuning models: {', '.join(models_to_tune)}")
    print("This may take a few minutes...")

    try:
        strategies = ["random", "grid"]

        for strategy in strategies:
            print(f"\n--- {strategy.upper()} SEARCH ---")

            summary = tuner.tune_models(
                X_train,
                y_train,
                models_to_tune=models_to_tune,
                search_type=strategy,
                n_iter=10 if strategy == "random" else 5,
                cv=3,
                register_best=True,
            )

            print(f"Tuning completed with {strategy} search")
            print("\nTuning Summary:")
            print(summary[["model", "best_score", "tuning_time", "status"]])

        best_models = tuner.get_best_models(top_n=3)
        print("\nTop 3 tuned models:")
        for i, model_info in enumerate(best_models, 1):
            print(f"{i}. {model_info['model_name']}: {model_info['best_score']:.4f}")
            print(f"   Strategy: {model_info['search_type']}")
            print(f"   Time: {model_info['tuning_time']:.2f}s")

    except Exception as e:
        print(f"Error during hyperparameter tuning: {e}")


def comprehensive_model_analysis(automl, X_test, y_test):
    """
    Perform comprehensive analysis of trained models
    """
    print("\n" + "=" * 60)
    print("COMPREHENSIVE MODEL ANALYSIS")
    print("=" * 60)

    print("\nGenerating comprehensive leaderboard...")
    try:
        leaderboard = automl.get_leaderboard()

        if not leaderboard.empty:
            print("\nModel Performance Leaderboard:")
            display_cols = [
                "model",
                "test_accuracy",
                "test_f1",
                "fit_quality",
                "training_time",
            ]
            available_cols = [col for col in display_cols if col in leaderboard.columns]
            print(leaderboard[available_cols].round(4))

            if "test_accuracy" in leaderboard.columns:
                best_model = leaderboard.loc[
                    leaderboard["test_accuracy"].idxmax(), "model"
                ]
                worst_model = leaderboard.loc[
                    leaderboard["test_accuracy"].idxmin(), "model"
                ]
                print(f"\n🏆 Best performer: {best_model}")
                print(f"⚠️  Needs improvement: {worst_model}")

    except Exception as e:
        print(f"Error generating leaderboard: {e}")

    print("\n" + "-" * 50)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("-" * 50)

    try:
        importance = automl.get_feature_importance()
        if importance:
            print("Feature importance from best model:")

            if "feature_importances_" in importance:
                importances = importance["feature_importances_"]
                feature_names = [f"feature_{i:02d}" for i in range(len(importances))]

                importance_df = pd.DataFrame(
                    {"feature": feature_names, "importance": importances}
                ).sort_values("importance", ascending=False)

                print("\nTop 10 most important features:")
                print(importance_df.head(10))

                print("\nFeature Importance Statistics:")
                print(f"  Mean importance: {importances.mean():.4f}")
                print(f"  Std importance: {importances.std():.4f}")
                print(f"  Top feature contributes: {importances.max():.2%}")
                print(
                    f"  Top 5 features contribute: {importances.nlargest(5).sum():.2%}"
                )

            elif "coefficients" in importance:
                coefficients = importance["coefficients"]
                print("Model uses coefficient-based importance (linear model)")
                print(f"Number of coefficients: {len(coefficients)}")
        else:
            print("No feature importance available for the best model")

    except Exception as e:
        print(f"Error in feature importance analysis: {e}")

    print("\n" + "-" * 50)
    print("PREDICTION ANALYSIS")
    print("-" * 50)

    try:
        predictions = automl.predict(X_test)

        print("Classification Report:")
        print(classification_report(y_test, predictions))

        cm = confusion_matrix(y_test, predictions)
        print("\nConfusion Matrix:")
        print(cm)

        try:
            probabilities = automl.predict_proba(X_test)
            confidence_scores = np.max(probabilities, axis=1)

            print("\nPrediction Confidence Analysis:")
            print(f"  Mean confidence: {confidence_scores.mean():.4f}")
            print(f"  Min confidence: {confidence_scores.min():.4f}")
            print(f"  Max confidence: {confidence_scores.max():.4f}")
            print(
                f"  Predictions with >90% confidence: {(confidence_scores > 0.9).sum()}/{len(confidence_scores)}"
            )

        except Exception:
            print("Prediction probabilities not available")

    except Exception as e:
        print(f"Error in prediction analysis: {e}")


def create_ensemble_model(automl, X_train, y_train):
    """
    Create an ensemble model from the best performers
    """
    print("\n" + "=" * 60)
    print("ENSEMBLE MODEL CREATION")
    print("=" * 60)

    try:
        leaderboard = automl.get_leaderboard()

        if leaderboard.empty:
            print("No models available for ensemble creation")
            return

        if "test_accuracy" in leaderboard.columns:
            top_models = leaderboard.nlargest(3, "test_accuracy")["model"].tolist()
        else:
            top_models = leaderboard["model"].head(3).tolist()

        print(f"Creating ensemble from top models: {top_models}")

        ensemble_estimators = []
        for model_name in top_models:
            print(f"  Including {model_name} in ensemble")

        print(f"✓ Ensemble would combine {len(top_models)} models")
        print(
            "Note: Full ensemble implementation requires model extraction from pipeline"
        )

    except Exception as e:
        print(f"Error creating ensemble: {e}")


def production_deployment_preparation(automl, output_dir="production_models"):
    """
    Prepare models for production deployment
    """
    print("\n" + "=" * 60)
    print("PRODUCTION DEPLOYMENT PREPARATION")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Preparing models for production in: {output_dir}")

    try:
        best_model_path = os.path.join(output_dir, "best_model.pkl")
        automl.save_best_model(best_model_path)
        print(f"✓ Best model saved: {best_model_path}")

        all_models_dir = os.path.join(output_dir, "all_models")
        automl.save_all_models(all_models_dir)
        print(f"✓ All models saved: {all_models_dir}")

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "best_model": automl.pipeline.best_model_name,
            "problem_type": automl.pipeline.problem_type,
            "framework_version": "0.1.0",
            "training_summary": automl.get_training_summary(),
        }

        leaderboard_path = os.path.join(output_dir, "model_leaderboard.csv")
        leaderboard = automl.get_leaderboard()
        leaderboard.to_csv(leaderboard_path, index=False)
        print(f"✓ Leaderboard saved: {leaderboard_path}")

        import json

        metadata_path = os.path.join(output_dir, "model_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        print(f"✓ Metadata saved: {metadata_path}")

        deployment_script = f"""#!/usr/bin/env python3
        '''
            Production deployment script for AutoML models
            Generated on: {datetime.now().isoformat()}
            '''

            import joblib
            import pandas as pd
            import numpy as np
            from automl import AutoML

            def load_model(model_path="{best_model_path}"):
                '''Load the trained AutoML model'''
                # Load the model wrapper
                model = joblib.load(model_path)
                return model

            def predict(model, X):
                '''Make predictions with the loaded model'''
                if isinstance(X, pd.DataFrame):
                    predictions = model.predict(X)
                else:
                    # Handle numpy arrays
                    predictions = model.predict(X)
                return predictions

            def predict_proba(model, X):
                '''Get prediction probabilities'''
                try:
                    probabilities = model.predict_proba(X)
                    return probabilities
                except AttributeError:
                    print("Model does not support probability predictions")
                    return None

            # Example usage
            if __name__ == "__main__":
                # Load model
                model = load_model()

                # Example prediction (replace with your data)
                # X_new = pd.read_csv('new_data.csv')
                # predictions = predict(model, X_new)
                # print(f"Predictions: {{predictions}}")

                print("Model loaded successfully and ready for deployment!")
        """

        deployment_script_path = os.path.join(output_dir, "deploy_model.py")
        with open(deployment_script_path, "w") as f:
            f.write(deployment_script)
        print(f"✓ Deployment script created: {deployment_script_path}")

        requirements_content = """# Production requirements for AutoML model deployment
            automl-framework>=0.1.0
            scikit-learn>=1.0.0
            pandas>=1.3.0
            numpy>=1.21.0
            joblib>=1.0.0

            # Optional dependencies (uncomment if needed)
            # scikit-optimize>=0.9.0  # For Bayesian optimization
            # hyperopt>=0.2.7         # For advanced hyperparameter tuning
        """

        requirements_path = os.path.join(output_dir, "requirements.txt")
        with open(requirements_path, "w") as f:
            f.write(requirements_content)
        print(f"✓ Requirements file created: {requirements_path}")

        deployment_readme = f"""# AutoML Model Deployment Package

            This package contains trained models and deployment utilities.

            ## Contents

            - `best_model.pkl` - The best performing model
            - `all_models/` - Directory containing all trained models
            - `model_leaderboard.csv` - Performance comparison of all models
            - `model_metadata.json` - Training metadata and configuration
            - `deploy_model.py` - Deployment script with example usage
            - `requirements.txt` - Python package dependencies

            ## Quick Start

            ```python
            # Load and use the model
            from deploy_model import load_model, predict

            model = load_model()
            predictions = predict(model, your_data)
            ```

            ## Model Information

            - **Best Model**: {automl.pipeline.best_model_name if automl.pipeline.best_model_name else 'Unknown'}
            - **Problem Type**: {automl.pipeline.problem_type}
            - **Training Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            - **Framework Version**: 0.1.0

            ## Performance Summary

            See `model_leaderboard.csv` for detailed performance metrics.

            ## Deployment Notes

            1. Ensure all dependencies are installed: `pip install -r requirements.txt`
            2. Test the model with your validation data before production use
            3. Monitor model performance and retrain when necessary
            4. Consider A/B testing when deploying new models

            ## Support

            For questions about model deployment, refer to the AutoML Framework documentation.
        """

        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(deployment_readme)
        print(f"✓ Deployment README created: {readme_path}")

        print("\n🚀 Production deployment package ready!")
        print(f"   Location: {os.path.abspath(output_dir)}")
        print("   Files created: 6")

    except Exception as e:
        print(f"Error preparing production deployment: {e}")


def visualization_demo(automl, X_test, y_test):
    """
    Create visualizations for model analysis
    """
    print("\n" + "=" * 60)
    print("VISUALIZATION DEMO")
    print("=" * 60)

    try:
        plt.style.use("default")
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(
            "AutoML Framework - Advanced Analysis", fontsize=16, fontweight="bold"
        )

        leaderboard = automl.get_leaderboard()
        if not leaderboard.empty and "test_accuracy" in leaderboard.columns:
            ax1 = axes[0, 0]
            models = leaderboard["model"].head(6)
            scores = leaderboard["test_accuracy"].head(6)

            bars = ax1.bar(range(len(models)), scores, color="skyblue", alpha=0.7)
            ax1.set_xlabel("Models")
            ax1.set_ylabel("Test Accuracy")
            ax1.set_title("Model Performance Comparison")
            ax1.set_xticks(range(len(models)))
            ax1.set_xticklabels(models, rotation=45, ha="right")

            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.005,
                    f"{score:.3f}",
                    ha="center",
                    va="bottom",
                )

        ax2 = axes[0, 1]
        try:
            fit_evaluations = automl.get_all_fit_evaluations()
            if fit_evaluations:
                model_names = []
                overfitting_scores = []

                for name, eval_data in fit_evaluations.items():
                    model_names.append(name[:10])
                    overfitting_scores.append(eval_data.get("overfitting_score", 0))

                colors = [
                    "red" if score > 0.3 else "orange" if score > 0.1 else "green"
                    for score in overfitting_scores
                ]

                bars = ax2.bar(
                    range(len(model_names)), overfitting_scores, color=colors, alpha=0.7
                )
                ax2.set_xlabel("Models")
                ax2.set_ylabel("Overfitting Score")
                ax2.set_title("Overfitting Detection")
                ax2.set_xticks(range(len(model_names)))
                ax2.set_xticklabels(model_names, rotation=45, ha="right")

                ax2.axhline(
                    y=0.1, color="orange", linestyle="--", alpha=0.7, label="Slight"
                )
                ax2.axhline(
                    y=0.3, color="red", linestyle="--", alpha=0.7, label="Moderate"
                )
                ax2.legend()
        except Exception:
            ax2.text(
                0.5,
                0.5,
                "Overfitting analysis\nnot available",
                ha="center",
                va="center",
                transform=ax2.transAxes,
            )
            ax2.set_title("Overfitting Detection")

        ax3 = axes[1, 0]
        try:
            importance = automl.get_feature_importance()
            if importance and "feature_importances_" in importance:
                importances = importance["feature_importances_"]
                feature_names = [f"F{i}" for i in range(len(importances))]

                top_indices = np.argsort(importances)[-10:]
                top_importances = importances[top_indices]
                top_features = [feature_names[i] for i in top_indices]

                bars = ax3.barh(
                    range(len(top_features)),
                    top_importances,
                    color="lightcoral",
                    alpha=0.7,
                )
                ax3.set_yticks(range(len(top_features)))
                ax3.set_yticklabels(top_features)
                ax3.set_xlabel("Importance")
                ax3.set_title("Top 10 Feature Importance")
            else:
                ax3.text(
                    0.5,
                    0.5,
                    "Feature importance\nnot available",
                    ha="center",
                    va="center",
                    transform=ax3.transAxes,
                )
                ax3.set_title("Feature Importance")
        except Exception:
            ax3.text(
                0.5,
                0.5,
                "Feature importance\nnot available",
                ha="center",
                va="center",
                transform=ax3.transAxes,
            )
            ax3.set_title("Feature Importance")

        ax4 = axes[1, 1]
        try:
            from sklearn.metrics import confusion_matrix

            predictions = automl.predict(X_test)
            cm = confusion_matrix(y_test, predictions)

            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax4)
            ax4.set_xlabel("Predicted")
            ax4.set_ylabel("Actual")
            ax4.set_title("Confusion Matrix (Best Model)")
        except Exception:
            ax4.text(
                0.5,
                0.5,
                "Confusion matrix\nnot available",
                ha="center",
                va="center",
                transform=ax4.transAxes,
            )
            ax4.set_title("Confusion Matrix")

        plt.tight_layout()

        viz_path = "advanced_automl_analysis.png"
        plt.savefig(viz_path, dpi=300, bbox_inches="tight")
        print(f"✓ Visualization saved: {viz_path}")

        plt.show()

    except Exception as e:
        print(f"Error creating visualizations: {e}")


def main():
    """
    Main function demonstrating advanced AutoML features
    """
    print("=" * 70)
    print("ADVANCED AUTOML FRAMEWORK DEMONSTRATION")
    print("=" * 70)
    print("This example showcases advanced features including:")
    print("• Custom model registration with specialized preprocessing")
    print("• Advanced overfitting detection and mitigation strategies")
    print("• Hyperparameter tuning with multiple optimization methods")
    print("• Comprehensive model analysis and comparison")
    print("• Production deployment preparation")
    print("• Advanced visualization and reporting")
    print("=" * 70)

    logger = setup_logging(level="INFO")

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    try:
        X, y = create_challenging_dataset()

        automl = advanced_model_registration_demo()

        X_train, X_test, y_train, y_test = overfitting_detection_demo(automl, X, y)

        hyperparameter_tuning_demo(automl, X_train, y_train)

        comprehensive_model_analysis(automl, X_test, y_test)

        create_ensemble_model(automl, X_train, y_train)

        production_deployment_preparation(automl)

        visualization_demo(automl, X_test, y_test)

        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 70)
        print("Key outputs generated:")
        print("• Trained models with overfitting mitigation")
        print("• Comprehensive performance analysis")
        print("• Production deployment package")
        print("• Advanced visualization plots")
        print("• Hyperparameter tuning results (if available)")
        print("\nNext steps:")
        print("• Review the generated analysis and visualizations")
        print("• Examine the production deployment package")
        print("• Adapt the patterns for your specific use case")
        print("• Consider the improvement suggestions for model optimization")

    except Exception as e:
        print(f"\n❌ Error in advanced example: {e}")
        import traceback

        traceback.print_exc()
        print("\nThis might be due to missing dependencies or data issues.")
        print("Try installing optional dependencies:")
        print("pip install scikit-optimize hyperopt")


if __name__ == "__main__":
    main()
