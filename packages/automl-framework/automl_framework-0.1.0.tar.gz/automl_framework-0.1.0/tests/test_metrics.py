"""
Tests for metrics calculator functionality
"""

import pytest
import numpy as np
from sklearn.datasets import make_classification

from automl.metrics import MetricsCalculator


class TestMetricsCalculator:
    """Test MetricsCalculator functionality"""

    def test_calculator_initialization(self):
        """Test metrics calculator initialization"""
        calc = MetricsCalculator(problem_type="classification")
        assert calc.problem_type == "classification"

        calc = MetricsCalculator(problem_type="regression")
        assert calc.problem_type == "regression"

    def test_binary_classification_metrics(self):
        """Test binary classification metrics"""
        calc = MetricsCalculator(problem_type="classification")

        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 0, 1])

        metrics = calc.calculate_metrics(y_true, y_pred)

        assert "accuracy" in metrics
        assert "f1_score" in metrics
        assert "recall" in metrics
        assert "precision" in metrics

        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["f1_score"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["precision"] <= 1

    def test_multiclass_classification_metrics(self):
        """Test multiclass classification metrics"""
        calc = MetricsCalculator(problem_type="classification")

        y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 2, 1, 0, 1, 2])

        metrics = calc.calculate_metrics(y_true, y_pred)

        assert "accuracy" in metrics
        assert "f1_score" in metrics
        assert "recall" in metrics
        assert "precision" in metrics

        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["f1_score"] <= 1

    def test_classification_with_probabilities(self):
        """Test classification metrics with probabilities"""
        calc = MetricsCalculator(problem_type="classification")

        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0])
        y_pred_proba = np.array([[0.8, 0.2], [0.3, 0.7], [0.9, 0.1], [0.6, 0.4]])

        metrics = calc.calculate_metrics(y_true, y_pred, y_pred_proba)

        assert "roc_auc" in metrics
        assert 0 <= metrics["roc_auc"] <= 1

    def test_classification_report(self):
        """Test classification report generation"""
        calc = MetricsCalculator(problem_type="classification")

        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 0, 1])

        report = calc.get_classification_report(y_true, y_pred)

        assert isinstance(report, str)
        assert "precision" in report
        assert "recall" in report
        assert "f1-score" in report

    def test_unsupported_problem_type(self):
        """Test unsupported problem type"""
        calc = MetricsCalculator(problem_type="regression")

        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([1.1, 2.1, 2.9])

        with pytest.raises(ValueError):
            calc.calculate_metrics(y_true, y_pred)
