"""
Metrics calculator for the AutoML framework.
Handles calculation and management of evaluation metrics.
"""

from typing import Dict
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    recall_score,
    precision_score,
    classification_report,
    roc_auc_score,
)


class MetricsCalculator:
    """Calculates and manages model evaluation metrics"""

    def __init__(self, problem_type: str = "classification"):
        self.problem_type = problem_type

    def calculate_metrics(self, y_true, y_pred, y_pred_proba=None) -> Dict[str, float]:
        """Calculate performance metrics based on problem type"""
        if self.problem_type == "classification":
            classes = np.unique(y_true)
            is_binary = len(classes) == 2

            metrics = {
                "accuracy": accuracy_score(y_true, y_pred),
            }

            if is_binary:
                metrics.update(
                    {
                        "f1_score": f1_score(y_true, y_pred),
                        "recall": recall_score(y_true, y_pred),
                        "precision": precision_score(y_true, y_pred),
                    }
                )

                if y_pred_proba is not None:
                    if y_pred_proba.shape[1] == 2:
                        metrics["roc_auc"] = roc_auc_score(y_true, y_pred_proba[:, 1])
            else:
                metrics.update(
                    {
                        "f1_score": f1_score(y_true, y_pred),
                        "recall": recall_score(y_true, y_pred),
                        "precision": precision_score(y_true, y_pred),
                    }
                )

                if y_pred_proba is not None:
                    metrics["roc_auc"] = roc_auc_score(
                        y_true, y_pred_proba, multi_class="ovr"
                    )

            return metrics
        else:
            raise ValueError(f"Unsupported problem type: {self.problem_type}")

    def get_classification_report(self, y_true, y_pred) -> str:
        """Get detailed classification report"""
        if self.problem_type != "classification":
            raise ValueError(
                "Classification report only available for classification problems"
            )

        return classification_report(y_true, y_pred)
