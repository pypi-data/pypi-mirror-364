"""
Integrated AutoML script that combines all AutoML functionality with overfitting handling.
Users just need to provide a dataframe and target column. Problem type is detected automatically.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import time
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import traceback

from automl import AutoML, DataUtils


def safe_evaluate(automl, X_test, y_test):
    """
    Safely evaluate models with better error handling

    Args:
        automl: The AutoML instance
        X_test: Test features
        y_test: Test target

    Returns:
        True if evaluation succeeded, False otherwise
    """
    try:
        automl.evaluate(X_test, y_test)
        return True
    except Exception as e:
        print(f"Error during model evaluation: {str(e)}")
        print(traceback.format_exc())
        print("Trying to continue with partial results...")

        if hasattr(automl.pipeline, "results") and automl.pipeline.results:
            print(f"Found {len(automl.pipeline.results)} evaluated models.")
            return True
        else:
            print("No models were successfully evaluated.")
            return False


def format_metric(metric):
    """
    Safely format a metric value, handling numpy arrays or other non-scalar types

    Args:
        metric: The metric value to format (could be float, numpy array, etc.)

    Returns:
        Formatted string representing the metric
    """
    import numpy as np

    if isinstance(metric, np.ndarray):
        if metric.size == 1:
            return f"{float(metric.item()):.4f}"
        elif metric.size > 1:
            return f"{float(np.mean(metric)):.4f} (mean)"
        else:
            return "N/A"
    elif metric is None:
        return "N/A"
    else:
        try:
            return f"{float(metric):.4f}"
        except Exception:
            return str(metric)


def display_enhanced_leaderboard(leaderboard, problem_type="classification"):
    """
    Display an enhanced leaderboard with better formatting

    Args:
        leaderboard: The model leaderboard DataFrame
        problem_type: 'classification' or 'regression'
    """
    import pandas as pd

    if leaderboard is None or leaderboard.empty:
        print("\nNo leaderboard available - evaluation did not produce results.")
        return

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    pd.set_option("display.precision", 4)
    pd.set_option("display.float_format", "{:.4f}".format)

    display_df = leaderboard.copy()

    if "training_time" in display_df.columns:
        display_df["training_time"] = display_df["training_time"].apply(
            lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
        )

    if problem_type == "classification":
        metric_groups = {
            "Accuracy": ["train_accuracy", "test_accuracy", "accuracy_gap"],
            "Precision": ["train_precision", "test_precision", "precision_gap"],
            "Recall": ["train_recall", "test_recall", "recall_gap"],
            "F1 Score": ["train_f1", "test_f1", "f1_gap"],
        }
    else:
        metric_groups = {
            "R²": ["train_r2", "test_r2", "r2_gap"],
            "MSE": ["train_mse", "test_mse", "mse_ratio"],
        }

    print("\nModel Leaderboard:")

    info_columns = [
        "model",
        "training_time",
        "fit_quality",
        "overfitting_score",
        "underfitting_score",
        "overfitting_severity",
    ]
    info_columns = [col for col in info_columns if col in display_df.columns]

    if info_columns:
        try:
            print(display_df[info_columns].to_string(index=True))
        except Exception as e:
            print(f"Could not display leaderboard info columns: {str(e)}")

    for group_name, columns in metric_groups.items():
        if any(col in display_df.columns for col in columns):
            existing_columns = [col for col in columns if col in display_df.columns]
            if existing_columns:
                try:
                    print(f"\n{group_name} Metrics:")
                    print(
                        display_df[["model"] + existing_columns].to_string(index=True)
                    )
                except Exception as e:
                    print(f"Could not display {group_name} metric group: {str(e)}")

    pd.reset_option("display.max_columns")
    pd.reset_option("display.width")
    pd.reset_option("display.precision")
    pd.reset_option("display.float_format")


def detect_problem_type(y):
    """
    Automatically detect if the problem is classification or regression.

    Args:
        y: Target variable (Series or array-like)

    Returns:
        str: 'classification' or 'regression'
    """
    if not isinstance(y, pd.Series):
        y = pd.Series(y)

    if pd.api.types.is_categorical_dtype(y) or pd.api.types.is_string_dtype(y):
        return "classification"

    unique_values = y.nunique()

    if unique_values <= 10:
        return "classification"

    if pd.api.types.is_integer_dtype(y) and y.equals(y.astype(int)):
        if unique_values <= 100:
            return "classification"

    if set(y.unique()).issubset(set(range(20))):
        return "classification"

    return "regression"


def run_automl(
    df,
    target_column,
    problem_type="auto",
    test_size=0.2,
    random_state=42,
    output_dir="models",
    handle_overfitting=True,
    auto_mitigate=True,
    overfitting_threshold=0.3,
    visualization=False,
):
    """
    Run the complete AutoML workflow with a single function call with overfitting handling.

    Args:
        df: DataFrame containing features and target
        target_column: Name of the target column in DataFrame
        problem_type: 'classification', 'regression', or 'auto' (detect automatically)
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        output_dir: Directory to save model and results
        handle_overfitting: Whether to enable overfitting detection
        auto_mitigate: Whether to automatically mitigate overfitting
        overfitting_threshold: Threshold for automatic mitigation (0.0-1.0)
        visualization: Whether to generate visualization plots

    Returns:
        Dictionary with results and trained AutoML object
    """
    print("Starting AutoML workflow with overfitting handling")
    start_time = time.time()

    os.makedirs(output_dir, exist_ok=True)

    print("\nPreparing data...")
    X = df.drop(columns=[target_column])
    y = df[target_column]

    if problem_type == "auto":
        problem_type = detect_problem_type(y)
        print(f"Auto-detected problem type: {problem_type}")

    print(f"Problem type: {problem_type}")

    print("Checking data quality...")
    data_report = DataUtils.check_data_quality(X, y)
    print("\nData Quality Report:")
    for key, value in data_report.items():
        if key == "class_distribution" and isinstance(value, dict) and len(value) > 10:
            print(f"- {key}: Too many classes to display")
        elif (
            key == "zero_variance_features"
            and isinstance(value, list)
            and len(value) > 10
        ):
            print(f"- {key}: {len(value)} features with zero variance")
        else:
            print(f"- {key}: {value}")

    print("\nSplitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y if problem_type == "classification" else None,
    )
    print(f"Training set: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    print(f"Test set: {X_test.shape[0]} samples, {X_test.shape[1]} features")

    print("\nInitializing AutoML...")
    config = {"problem_type": problem_type, "random_state": random_state}
    automl = AutoML(config)

    if handle_overfitting and hasattr(automl.pipeline, "set_overfitting_control"):
        print("Enabling overfitting detection and mitigation...")
        automl.pipeline.set_overfitting_control(
            detection_enabled=handle_overfitting,
            auto_mitigation=auto_mitigate,
            threshold=overfitting_threshold,
        )

    print("\nTraining models...")
    train_start = time.time()
    automl.fit(X_train, y_train)
    train_end = time.time()
    print(f"Training completed in {train_end - train_start:.2f} seconds")

    training_summary = automl.get_training_summary()
    print("\nTraining Summary:")
    print(f"- Models trained: {training_summary['n_models_trained']}")
    print(f"- Successful models: {len(training_summary['successful_models'])}")
    print(f"- Failed models: {len(training_summary['failed_models'])}")

    if handle_overfitting and "mitigated_models" in training_summary:
        print(
            f"- Models mitigated for overfitting: {len(training_summary['mitigated_models'])}"
        )

    print("\nEvaluating models...")
    evaluation_succeeded = safe_evaluate(automl, X_test, y_test)

    leaderboard = None
    try:
        if (
            evaluation_succeeded
            and hasattr(automl.pipeline, "results")
            and automl.pipeline.results
        ):
            leaderboard = automl.get_leaderboard()
            display_enhanced_leaderboard(leaderboard, problem_type)

            mitigated_models = []
            if leaderboard is not None:
                mitigated_models = [
                    model
                    for model in leaderboard["model"]
                    if str(model).find("mitigated") != -1
                ]
            if mitigated_models:
                print(
                    f"\nMitigated models in leaderboard: {', '.join(str(m) for m in mitigated_models)}"
                )
        else:
            print("\nSkipping leaderboard due to evaluation errors or no results.")
    except Exception as e:
        print(f"Could not display leaderboard: {str(e)}")
        print(traceback.format_exc())
        print("Continuing with analysis...")

    print("\nFit Quality and Overfitting Analysis:")
    try:
        all_evaluations = automl.get_all_fit_evaluations()

        overfitting_assessments = {}
        if handle_overfitting and hasattr(
            automl.pipeline, "get_all_overfitting_assessments"
        ):
            overfitting_assessments = automl.pipeline.get_all_overfitting_assessments()

        for model_name, eval_data in all_evaluations.items():
            fit_quality = eval_data.get("fit_quality", "Unknown")

            if fit_quality == "Good fit" and not (
                model_name in overfitting_assessments
                and overfitting_assessments[model_name].get("is_overfitting", False)
            ):
                continue

            print(f"\n{model_name}:")
            print(f"- Fit Quality: {fit_quality}")
            print(
                f"- Overfitting Score: {format_metric(eval_data.get('overfitting_score', 0))}"
            )
            print(
                f"- Underfitting Score: {format_metric(eval_data.get('underfitting_score', 0))}"
            )

            if model_name in overfitting_assessments:
                assessment = overfitting_assessments[model_name]
                if assessment.get("is_overfitting", False):
                    print(
                        f"- Overfitting Severity: {assessment.get('severity', 'Unknown')}"
                    )

                    details = assessment.get("details", {})
                    if details:
                        if "accuracy_gap" in details:
                            print(
                                f"  * Accuracy Gap: {format_metric(details['accuracy_gap'])}"
                            )
                        if "precision_gap" in details:
                            print(
                                f"  * Precision Gap: {format_metric(details['precision_gap'])}"
                            )
                        if "recall_gap" in details:
                            print(
                                f"  * Recall Gap: {format_metric(details['recall_gap'])}"
                            )

            try:
                suggestions = automl.get_improvement_suggestions(model_name)
                if suggestions:
                    print("- Improvement Suggestions:")
                    for i, suggestion in enumerate(suggestions[:3], 1):
                        print(f"  {i}. {suggestion}")
            except Exception as e:
                print(f"- Could not get improvement suggestions: {str(e)}")
    except Exception as e:
        print(f"Error in fit quality analysis: {str(e)}")
        print(traceback.format_exc())

    try:
        if handle_overfitting and hasattr(automl.pipeline, "get_mitigated_models"):
            mitigated_models_info = automl.pipeline.get_mitigated_models()
            if mitigated_models_info:
                print("\nModels Mitigated for Overfitting:")
                for name, info in mitigated_models_info.items():
                    print(
                        f"- {name}: Applied {info['strategy']} strategy to {info['original_model']}"
                    )
    except Exception as e:
        print(f"Error getting mitigated models info: {str(e)}")

    best_model_name = None
    best_model_path = None

    if hasattr(automl.pipeline, "best_model_name"):
        best_model_name = automl.pipeline.best_model_name

    if best_model_name:
        print(f"\nBest Model: {best_model_name}")

        is_mitigated = str(best_model_name).find("mitigated") != -1
        if is_mitigated:
            print("(This is a mitigated model with improved generalization)")

        try:
            best_eval = automl.get_fit_evaluation(best_model_name)
            print(f"- Fit Quality: {best_eval.get('fit_quality', 'Unknown')}")

            if problem_type == "classification":
                y_pred = automl.predict(X_test)
                from sklearn.metrics import (
                    accuracy_score,
                    f1_score,
                    precision_score,
                    recall_score,
                )

                accuracy = accuracy_score(y_test, y_pred)

                is_binary = len(np.unique(y)) <= 2
                average = None if is_binary else "weighted"

                f1 = f1_score(y_test, y_pred, average=average)
                precision = precision_score(y_test, y_pred, average=average)
                recall = recall_score(y_test, y_pred, average=average)

                print(f"- Test Accuracy: {format_metric(accuracy)}")
                print(f"- Test F1 Score: {format_metric(f1)}")
                print(f"- Test Precision: {format_metric(precision)}")
                print(f"- Test Recall: {format_metric(recall)}")

                try:
                    y_train_pred = automl.predict(X_train)
                    train_accuracy = accuracy_score(y_train, y_train_pred)
                    train_f1 = f1_score(y_train, y_train_pred, average=average)
                    train_precision = precision_score(
                        y_train, y_train_pred, average=average
                    )
                    train_recall = recall_score(y_train, y_train_pred, average=average)

                    print(f"- Train Accuracy: {format_metric(train_accuracy)}")
                    print(f"- Train F1 Score: {format_metric(train_f1)}")
                    print(f"- Train Precision: {format_metric(train_precision)}")
                    print(f"- Train Recall: {format_metric(train_recall)}")

                    print(
                        f"- Accuracy Gap (Train-Test): {format_metric(train_accuracy - accuracy)}"
                    )
                    print(f"- F1 Gap (Train-Test): {format_metric(train_f1 - f1)}")
                except Exception as e:
                    print(f"Could not calculate training metrics: {str(e)}")

            else:
                y_pred = automl.predict(X_test)
                from sklearn.metrics import (
                    mean_squared_error,
                    r2_score,
                    mean_absolute_error,
                )

                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)

                print(f"- Test MSE: {format_metric(mse)}")
                print(f"- Test RMSE: {format_metric(rmse)}")
                print(f"- Test R² Score: {format_metric(r2)}")
                print(f"- Test MAE: {format_metric(mae)}")

                try:
                    y_train_pred = automl.predict(X_train)
                    train_mse = mean_squared_error(y_train, y_train_pred)
                    train_r2 = r2_score(y_train, y_train_pred)

                    print(f"- Train MSE: {format_metric(train_mse)}")
                    print(f"- Train R² Score: {format_metric(train_r2)}")

                    mse_ratio = mse / train_mse if train_mse > 0 else "N/A"
                    if mse_ratio != "N/A":
                        print(f"- MSE Ratio (Test/Train): {format_metric(mse_ratio)}")
                    else:
                        print(f"- MSE Ratio (Test/Train): {mse_ratio}")

                    print(f"- R² Gap (Train-Test): {format_metric(train_r2 - r2)}")
                except Exception as e:
                    print(f"Could not calculate training metrics: {str(e)}")
        except Exception as e:
            print(f"Error getting best model evaluation: {str(e)}")

        try:
            best_model_path = os.path.join(output_dir, "best_model.pkl")
            automl.save_best_model(best_model_path)
            print(f"\nBest model saved to: {best_model_path}")
        except Exception as e:
            print(f"Error saving best model: {str(e)}")

    try:
        feature_importance = automl.get_feature_importance()
        if feature_importance and (
            "feature_importances_" in feature_importance
            or "coefficients" in feature_importance
        ):
            print("\nFeature Importance (Top 10):")

            if "feature_importances_" in feature_importance:
                importances = feature_importance["feature_importances_"]
            else:
                importances = feature_importance["coefficients"]
                if hasattr(importances, "flatten"):
                    importances = importances.flatten()

            try:
                importance_df = pd.DataFrame(
                    {"Feature": X.columns, "Importance": np.abs(importances)}
                ).sort_values("Importance", ascending=False)

                print(importance_df.head(10))

                importance_df.to_csv(
                    os.path.join(output_dir, "feature_importance.csv"), index=False
                )

                if visualization:
                    plt.figure(figsize=(10, 6))
                    sns.barplot(
                        x="Importance", y="Feature", data=importance_df.head(15)
                    )
                    plt.title("Top 15 Features by Importance")
                    plt.tight_layout()
                    plt.savefig(os.path.join(output_dir, "feature_importance.png"))
            except Exception as e:
                print(f"Error creating feature importance visualization: {str(e)}")
                print(traceback.format_exc())
    except Exception as e:
        print(f"Error getting feature importance: {str(e)}")

    if visualization and handle_overfitting:
        print("\nGenerating overfitting visualization...")
        try:
            model_data = []
            for model_name, eval_data in all_evaluations.items():
                if problem_type == "classification":
                    if not all(
                        k in eval_data for k in ["train_accuracy", "test_accuracy"]
                    ):
                        continue
                else:
                    if not all(k in eval_data for k in ["train_r2", "test_r2"]):
                        continue

                if problem_type == "classification":
                    train_score = eval_data.get("train_accuracy", 0)
                    test_score = eval_data.get("test_accuracy", 0)
                else:
                    train_score = eval_data.get("train_r2", 0)
                    test_score = eval_data.get("test_r2", 0)

                if (
                    hasattr(train_score, "__len__")
                    and not isinstance(train_score, (str, dict))
                    and len(train_score) > 1
                ):
                    train_score = float(np.mean(train_score))
                if (
                    hasattr(test_score, "__len__")
                    and not isinstance(test_score, (str, dict))
                    and len(test_score) > 1
                ):
                    test_score = float(np.mean(test_score))

                row = {
                    "Model": model_name,
                    "Train Score": train_score,
                    "Test Score": test_score,
                    "Overfitting Score": eval_data.get("overfitting_score", 0),
                }
                row["Gap"] = row["Train Score"] - row["Test Score"]
                model_data.append(row)

            if model_data:
                plot_df = pd.DataFrame(model_data)

                plot_df = plot_df.sort_values("Overfitting Score", ascending=False)

                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

                plot_df.plot(
                    x="Model", y=["Train Score", "Test Score"], kind="bar", ax=ax1
                )
                ax1.set_title("Train vs Test Performance")
                ax1.set_ylabel("Score")
                ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")

                plot_df.plot(
                    x="Model", y="Overfitting Score", kind="bar", ax=ax2, color="orange"
                )
                ax2.set_title("Overfitting Score by Model")
                ax2.set_ylabel("Overfitting Score")
                ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right")

                ax2.axhline(y=0.1, linestyle="--", color="green", alpha=0.7)
                ax2.axhline(y=0.3, linestyle="--", color="orange", alpha=0.7)
                ax2.axhline(y=0.6, linestyle="--", color="red", alpha=0.7)

                ax2.text(len(plot_df) - 1, 0.11, "Slight", color="green", ha="right")
                ax2.text(len(plot_df) - 1, 0.31, "Moderate", color="orange", ha="right")
                ax2.text(len(plot_df) - 1, 0.61, "Severe", color="red", ha="right")

                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, "overfitting_analysis.png"))
                print(
                    f"Saved overfitting visualization to: {os.path.join(output_dir, 'overfitting_analysis.png')}"
                )
        except Exception as e:
            print(f"Could not generate visualization: {str(e)}")
            print(traceback.format_exc())

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

    results = {
        "automl": automl,
        "leaderboard": leaderboard,
        "best_model_name": best_model_name,
        "best_model_path": best_model_path,
        "feature_importance": (
            feature_importance if "feature_importance" in locals() else None
        ),
        "training_summary": training_summary,
        "execution_time": total_time,
        "problem_type": problem_type,
    }

    if handle_overfitting:
        if "overfitting_assessments" in locals():
            results["overfitting_assessments"] = overfitting_assessments
        else:
            results["overfitting_assessments"] = {}

        if hasattr(automl.pipeline, "get_mitigated_models"):
            try:
                results["mitigated_models"] = automl.pipeline.get_mitigated_models()
            except Exception:
                results["mitigated_models"] = {}

    return results
