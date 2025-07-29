"""
Enhanced model evaluation utilities for the AutoML framework.
Provides improved functions for detecting overfitting and underfitting
with focus on precision, recall, and test set performance.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
import logging

logger = logging.getLogger("AutoML")


class ModelEvaluator:
    """Evaluates models for overfitting and underfitting with enhanced metrics"""

    def __init__(self, problem_type: str = "classification"):
        """
        Initialize the evaluator

        Args:
            problem_type: Type of problem ('classification' or 'regression')
        """
        self.problem_type = problem_type

    def _safe_scalar(self, x):
        """Convert array metrics to scalar values by taking the mean"""
        if x is None:
            return 0.0
        if hasattr(x, "shape") and len(getattr(x, "shape", [])) > 0 and x.shape[0] > 1:
            return float(np.mean(x))
        if hasattr(x, "__len__") and not isinstance(x, (str, dict)) and len(x) > 1:
            return float(np.mean(x))
        try:
            return float(x)
        except (TypeError, ValueError):
            return 0.0

    def _safe_diff(self, train_metric, test_metric):
        """Safely calculate differences between metrics that could be arrays"""
        train_scalar = self._safe_scalar(train_metric)
        test_scalar = self._safe_scalar(test_metric)
        return max(0, train_scalar - test_scalar)

    """
    Enhanced model evaluation method to collect comprehensive train/test metrics.
    """

    def evaluate_model_fit(
        self, model, X_train, y_train, X_test, y_test
    ) -> Dict[str, Any]:
        """
        Evaluate a model for overfitting or underfitting with comprehensive metrics

        Args:
            model: The model to evaluate
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary with evaluation metrics including train/test comparisons
        """
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        try:
            y_train_proba = model.predict_proba(X_train)
            y_test_proba = model.predict_proba(X_test)
        except Exception:
            y_train_proba = None
            y_test_proba = None

        if self.problem_type == "classification":
            return self._evaluate_classification_fit(
                y_train, y_train_pred, y_train_proba, y_test, y_test_pred, y_test_proba
            )
        else:
            return self._evaluate_regression_fit(
                y_train, y_train_pred, y_test, y_test_pred
            )

    def _evaluate_classification_fit(
        self, y_train, y_train_pred, y_train_proba, y_test, y_test_pred, y_test_proba
    ) -> Dict[str, Any]:
        """
        Evaluate classification model fit with comprehensive metrics

        Returns:
            Dictionary with detailed classification metrics for train and test sets
        """
        from sklearn.metrics import (
            accuracy_score,
            f1_score,
            precision_score,
            recall_score,
            roc_auc_score,
            confusion_matrix,
        )
        import numpy as np

        is_binary = len(np.unique(np.concatenate([y_train, y_test]))) <= 2
        average = None if is_binary else "weighted"

        train_accuracy = accuracy_score(y_train, y_train_pred)
        train_precision = precision_score(y_train, y_train_pred, average=average)
        train_recall = recall_score(y_train, y_train_pred, average=average)
        train_f1 = f1_score(y_train, y_train_pred, average=average)

        test_accuracy = accuracy_score(y_test, y_test_pred)
        test_precision = precision_score(y_test, y_test_pred, average=average)
        test_recall = recall_score(y_test, y_test_pred, average=average)
        test_f1 = f1_score(y_test, y_test_pred, average=average)

        train_roc_auc = None
        test_roc_auc = None

        if y_train_proba is not None and y_test_proba is not None:
            try:
                if is_binary:
                    if y_train_proba.shape[1] == 2:
                        train_roc_auc = roc_auc_score(y_train, y_train_proba[:, 1])
                        test_roc_auc = roc_auc_score(y_test, y_test_proba[:, 1])
                    else:
                        train_roc_auc = roc_auc_score(y_train, y_train_proba)
                        test_roc_auc = roc_auc_score(y_test, y_test_proba)
                else:
                    train_roc_auc = roc_auc_score(
                        y_train, y_train_proba, multi_class="ovr", average="weighted"
                    )
                    test_roc_auc = roc_auc_score(
                        y_test, y_test_proba, multi_class="ovr", average="weighted"
                    )
            except Exception as e:
                logger.warning(f"Could not calculate ROC AUC: {str(e)}")

        train_cm = confusion_matrix(y_train, y_train_pred)
        test_cm = confusion_matrix(y_test, y_test_pred)

        train_accuracy_scalar = self._safe_scalar(train_accuracy)
        test_accuracy_scalar = self._safe_scalar(test_accuracy)
        train_precision_scalar = self._safe_scalar(train_precision)
        test_precision_scalar = self._safe_scalar(test_precision)
        train_recall_scalar = self._safe_scalar(train_recall)
        test_recall_scalar = self._safe_scalar(test_recall)
        train_f1_scalar = self._safe_scalar(train_f1)
        test_f1_scalar = self._safe_scalar(test_f1)

        accuracy_diff = train_accuracy_scalar - test_accuracy_scalar
        precision_diff = train_precision_scalar - test_precision_scalar
        recall_diff = train_recall_scalar - test_recall_scalar
        f1_diff = train_f1_scalar - test_f1_scalar

        result = {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "accuracy_diff": accuracy_diff,
            "train_precision": train_precision,
            "test_precision": test_precision,
            "precision_diff": precision_diff,
            "train_recall": train_recall,
            "test_recall": test_recall,
            "recall_diff": recall_diff,
            "train_f1": train_f1,
            "test_f1": test_f1,
            "f1_diff": f1_diff,
            "train_confusion_matrix": train_cm,
            "test_confusion_matrix": test_cm,
        }

        if train_roc_auc is not None and test_roc_auc is not None:
            result["train_roc_auc"] = train_roc_auc
            result["test_roc_auc"] = test_roc_auc
            result["roc_auc_diff"] = self._safe_scalar(
                train_roc_auc
            ) - self._safe_scalar(test_roc_auc)

        overfitting_score = self._calculate_overfitting_score(
            train_accuracy=train_accuracy,
            test_accuracy=test_accuracy,
            train_precision=train_precision,
            test_precision=test_precision,
            train_recall=train_recall,
            test_recall=test_recall,
            train_f1=train_f1,
            test_f1=test_f1,
        )

        underfitting_score = self._calculate_underfitting_score(
            train_accuracy=train_accuracy,
            test_accuracy=test_accuracy,
            test_precision=test_precision,
            test_recall=test_recall,
        )

        result["overfitting_score"] = overfitting_score
        result["underfitting_score"] = underfitting_score

        result["fit_quality"] = self._determine_fit_quality(
            overfitting_score, underfitting_score
        )

        return result

    """
    Additional fix for regression model evaluation in _evaluate_regression_fit function.
    """

    def _evaluate_regression_fit(
        self, y_train, y_train_pred, y_test, y_test_pred
    ) -> Dict[str, Any]:
        """
        Evaluate regression model fit with safe calculations for arrays

        Returns:
            Dictionary with regression metrics
        """
        import numpy as np
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)

        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)

        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)

        train_mse_scalar = self._safe_scalar(train_mse)
        test_mse_scalar = self._safe_scalar(test_mse)
        train_r2_scalar = self._safe_scalar(train_r2)
        test_r2_scalar = self._safe_scalar(test_r2)

        r2_diff = train_r2_scalar - test_r2_scalar
        mse_ratio = (
            test_mse_scalar / train_mse_scalar if train_mse_scalar > 0 else float("inf")
        )

        result = {
            "train_mse": train_mse,
            "test_mse": test_mse,
            "train_mae": train_mae,
            "test_mae": test_mae,
            "train_r2": train_r2,
            "test_r2": test_r2,
            "mse_ratio": mse_ratio,
            "r2_diff": r2_diff,
        }

        r2_overfitting = min(max(0, r2_diff) / 0.3, 1.0)

        if mse_ratio > 1:
            mse_overfitting = min(max(0, np.log10(mse_ratio)) / 2, 1.0)
        else:
            mse_overfitting = 0

        overfitting_score = 0.6 * r2_overfitting + 0.4 * mse_overfitting

        if train_r2_scalar < 0.5:
            underfitting_score = 1.0 - max(0, train_r2_scalar) / 0.5
        else:
            underfitting_score = 0.0

        result["overfitting_score"] = overfitting_score
        result["underfitting_score"] = underfitting_score

        result["fit_quality"] = self._determine_fit_quality(
            overfitting_score, underfitting_score
        )

        return result

    """
    Fixed _calculate_overfitting_score method to handle array metrics properly.
    """

    def _calculate_overfitting_score(
        self,
        train_accuracy,
        test_accuracy,
        train_precision,
        test_precision,
        train_recall,
        test_recall,
        train_f1,
        test_f1,
        accuracy_weight=0.4,
        precision_weight=0.2,
        recall_weight=0.2,
        f1_weight=0.2,
        threshold=0.1,
    ):
        """
        Calculate a comprehensive overfitting score using multiple metrics

        Args:
            train_* and test_* metrics for accuracy, precision, recall, f1
            weights for each metric
            threshold: Threshold for significant difference

        Returns:
            Overfitting score between 0 and 1
        """
        accuracy_diff = self._safe_diff(train_accuracy, test_accuracy)
        precision_diff = self._safe_diff(train_precision, test_precision)
        recall_diff = self._safe_diff(train_recall, test_recall)
        f1_diff = self._safe_diff(train_f1, test_f1)

        normalized_acc_diff = min(accuracy_diff / threshold, 1.0)
        normalized_prec_diff = min(precision_diff / threshold, 1.0)
        normalized_recall_diff = min(recall_diff / threshold, 1.0)
        normalized_f1_diff = min(f1_diff / threshold, 1.0)

        overfitting_score = (
            accuracy_weight * normalized_acc_diff
            + precision_weight * normalized_prec_diff
            + recall_weight * normalized_recall_diff
            + f1_weight * normalized_f1_diff
        )

        return overfitting_score

    def _calculate_underfitting_score(
        self,
        train_accuracy,
        test_accuracy,
        test_precision,
        test_recall,
        train_threshold: float = 0.7,
        test_threshold: float = 0.65,
        train_weight: float = 0.3,
        test_weight: float = 0.7,
    ) -> float:
        """
        Calculate underfitting score based on both training and test performance

        Args:
            train_accuracy: Accuracy on training data
            test_accuracy: Accuracy on test data
            test_precision: Precision on test data
            test_recall: Recall on test data
            train_threshold: Minimum acceptable training performance
            test_threshold: Minimum acceptable test performance
            train_weight: Weight for training performance
            test_weight: Weight for test performance

        Returns:
            Underfitting score between 0 and 1
        """
        train_accuracy_scalar = self._safe_scalar(train_accuracy)
        test_accuracy_scalar = self._safe_scalar(test_accuracy)
        test_precision_scalar = self._safe_scalar(test_precision)
        test_recall_scalar = self._safe_scalar(test_recall)

        if train_accuracy_scalar >= train_threshold:
            train_underfitting = 0.0
        else:
            train_underfitting = 1.0 - (train_accuracy_scalar / train_threshold)

        test_metrics_avg = (
            test_accuracy_scalar + test_precision_scalar + test_recall_scalar
        ) / 3
        if test_metrics_avg >= test_threshold:
            test_underfitting = 0.0
        else:
            test_underfitting = 1.0 - (test_metrics_avg / test_threshold)

        underfitting_score = (
            train_weight * train_underfitting + test_weight * test_underfitting
        )

        return underfitting_score

    def _determine_fit_quality(
        self, overfitting_score: float, underfitting_score: float
    ) -> str:
        """
        Determine the overall fit quality

        Args:
            overfitting_score: Score indicating overfitting
            underfitting_score: Score indicating underfitting

        Returns:
            String describing fit quality
        """
        overfitting_score = self._safe_scalar(overfitting_score)
        underfitting_score = self._safe_scalar(underfitting_score)

        if overfitting_score < 0.1 and underfitting_score < 0.1:
            return "Good fit"
        elif overfitting_score >= 0.7:
            return "Severe overfitting"
        elif underfitting_score >= 0.7:
            return "Severe underfitting"
        elif overfitting_score >= 0.4 and overfitting_score > underfitting_score:
            return "Moderate overfitting"
        elif underfitting_score >= 0.4 and underfitting_score >= overfitting_score:
            return "Moderate underfitting"
        elif overfitting_score > underfitting_score:
            return "Slight overfitting"
        else:
            return "Slight underfitting"

    def get_improvement_suggestions(
        self, evaluation_results: Dict[str, Any]
    ) -> List[str]:
        """
        Generate suggestions for improving the model based on evaluation results

        Args:
            evaluation_results: Results from evaluate_model_fit

        Returns:
            List of improvement suggestions
        """
        suggestions = []
        fit_quality = evaluation_results.get("fit_quality", "")

        high_precision_low_recall = False
        low_precision_high_recall = False

        if (
            "test_precision" in evaluation_results
            and "test_recall" in evaluation_results
        ):
            test_precision = self._safe_scalar(evaluation_results["test_precision"])
            test_recall = self._safe_scalar(evaluation_results["test_recall"])
            precision_recall_gap = abs(test_precision - test_recall)

            if precision_recall_gap > 0.2:
                if test_precision > test_recall:
                    high_precision_low_recall = True
                else:
                    low_precision_high_recall = True

        if "overfitting" in fit_quality.lower():
            suggestions.extend(
                [
                    "Try regularization techniques (L1, L2, ElasticNet)",
                    "Reduce model complexity/depth",
                    "Use early stopping",
                    "Apply dropout or pruning",
                    "Collect more training data",
                    "Use data augmentation techniques",
                ]
            )

            if high_precision_low_recall:
                suggestions.append(
                    "Model may be too conservative - adjust decision threshold or class weights"
                )
            elif low_precision_high_recall:
                suggestions.append(
                    "Model may be making too many positive predictions - consider rebalancing training data"
                )

        if "underfitting" in fit_quality.lower():
            suggestions.extend(
                [
                    "Increase model complexity",
                    "Add more features or create new features",
                    "Reduce regularization",
                    "Train for more epochs/iterations",
                    "Try a more complex model architecture",
                    "Consider ensemble methods",
                ]
            )

            if "test_accuracy" in evaluation_results:
                test_accuracy = self._safe_scalar(evaluation_results["test_accuracy"])
                if test_accuracy < 0.6:
                    suggestions.append(
                        "Test performance is poor - model may need a complete reassessment"
                    )

        if not suggestions:
            suggestions.append(
                "Model seems to be well-balanced. Consider fine-tuning hyperparameters for small improvements."
            )

        return suggestions
