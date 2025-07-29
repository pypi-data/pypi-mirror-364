"""
Tests for overfitting detection and mitigation functionality
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from automl.overfitting_handler import OverfittingHandler
from automl.utils import DataUtils


class TestOverfittingHandler:
    """Test overfitting detection and mitigation"""

    def test_handler_initialization(self):
        """Test overfitting handler initialization"""
        handler = OverfittingHandler(problem_type="classification")
        assert handler.problem_type == "classification"

        handler = OverfittingHandler(problem_type="regression")
        assert handler.problem_type == "regression"

    def test_overfitting_detection_classification(self, overfitting_prone_data):
        """Test overfitting detection for classification"""
        X, y = overfitting_prone_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.4, random_state=42
        )

        model = DecisionTreeClassifier(random_state=42)
        model.fit(X_train, y_train)

        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
        )

        train_metrics = {
            "accuracy": accuracy_score(y_train, train_pred),
            "precision": precision_score(y_train, train_pred, average="weighted"),
            "recall": recall_score(y_train, train_pred, average="weighted"),
            "f1": f1_score(y_train, train_pred, average="weighted"),
        }

        test_metrics = {
            "accuracy": accuracy_score(y_test, test_pred),
            "precision": precision_score(y_test, test_pred, average="weighted"),
            "recall": recall_score(y_test, test_pred, average="weighted"),
            "f1": f1_score(y_test, test_pred, average="weighted"),
        }

        result = handler.detect_overfitting(train_metrics, test_metrics, "DecisionTree")

        assert isinstance(result, dict)
        assert "is_overfitting" in result
        assert "overfitting_score" in result
        assert "severity" in result
        assert "details" in result

        assert isinstance(result["is_overfitting"], bool)
        assert isinstance(result["overfitting_score"], float)
        assert result["overfitting_score"] >= 0
        assert result["severity"] in ["None", "Slight", "Moderate", "Severe"]

    def test_overfitting_detection_regression(self, sample_regression_data):
        """Test overfitting detection for regression"""
        X, y = sample_regression_data
        handler = OverfittingHandler(problem_type="regression")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(n_estimators=100, max_depth=None, random_state=42)
        model.fit(X_train, y_train)

        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

        train_metrics = {
            "mse": mean_squared_error(y_train, train_pred),
            "rmse": np.sqrt(mean_squared_error(y_train, train_pred)),
            "mae": mean_absolute_error(y_train, train_pred),
            "r2": r2_score(y_train, train_pred),
        }

        test_metrics = {
            "mse": mean_squared_error(y_test, test_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, test_pred)),
            "mae": mean_absolute_error(y_test, test_pred),
            "r2": r2_score(y_test, test_pred),
        }

        result = handler.detect_overfitting(
            train_metrics, test_metrics, "RandomForestRegressor"
        )

        assert isinstance(result, dict)
        assert "is_overfitting" in result
        assert "overfitting_score" in result
        assert "severity" in result
        assert "details" in result
        assert "r2_gap" in result["details"]
        assert "mse_ratio" in result["details"]

    def test_model_specific_risks(self):
        """Test model-specific overfitting risk assessment"""
        handler = OverfittingHandler()

        high_variance_models = [
            "DecisionTree",
            "RandomForest",
            "GradientBoosting",
            "XGBoost",
        ]
        for model_name in high_variance_models:
            risks = handler._check_model_specific_risks(model_name)
            assert risks["high_variance_model"] == True

        complex_models = ["MLPClassifier", "NeuralNetwork", "DeepLearning"]
        for model_name in complex_models:
            risks = handler._check_model_specific_risks(model_name)
            assert risks["complex_model"] == True

        flexible_models = ["SVM", "SVC", "SVR"]
        for model_name in flexible_models:
            risks = handler._check_model_specific_risks(model_name)
            assert risks["flexible_model"] == True

    def test_prevention_parameters(self):
        """Test getting prevention parameters for different models"""
        handler = OverfittingHandler()

        dt_params = handler.get_prevention_params("DecisionTree")
        assert "max_depth" in dt_params
        assert "min_samples_split" in dt_params
        assert "min_samples_leaf" in dt_params

        rf_params = handler.get_prevention_params("RandomForest")
        assert "max_depth" in rf_params
        assert "min_samples_split" in rf_params
        assert "bootstrap" in rf_params

        gb_params = handler.get_prevention_params("GradientBoosting")
        assert "learning_rate" in gb_params
        assert "n_estimators" in gb_params
        assert "max_depth" in gb_params

        lr_params = handler.get_prevention_params("LogisticRegression")
        assert "C" in lr_params
        assert "penalty" in lr_params

        svm_params = handler.get_prevention_params("SVM")
        assert "C" in svm_params
        assert "kernel" in svm_params
        assert "gamma" in svm_params

    def test_mitigation_strategies(self):
        """Test getting mitigation strategies"""
        handler = OverfittingHandler()

        overfitting_data = {
            "is_overfitting": True,
            "severity": "Moderate",
            "overfitting_score": 0.4,
            "model_specific": {
                "high_variance_model": True,
                "complex_model": False,
                "flexible_model": False,
            },
        }

        strategies = handler.get_mitigation_strategies("RandomForest", overfitting_data)

        assert isinstance(strategies, list)
        assert len(strategies) > 0

        for strategy in strategies:
            assert "name" in strategy
            assert "description" in strategy
            assert "priority" in strategy

    def test_regularization_params(self):
        """Test regularization parameter generation"""
        handler = OverfittingHandler()

        severities = ["Severe", "Moderate", "Slight"]

        for severity in severities:
            dt_params = handler._get_regularization_params("DecisionTree", severity)
            assert "max_depth" in dt_params
            assert "min_samples_split" in dt_params

            rf_params = handler._get_regularization_params("RandomForest", severity)
            assert "max_depth" in rf_params
            assert "min_samples_split" in rf_params

            gb_params = handler._get_regularization_params("GradientBoosting", severity)
            assert "learning_rate" in gb_params
            assert "max_depth" in gb_params

            lr_params = handler._get_regularization_params(
                "LogisticRegression", severity
            )
            assert "C" in lr_params
            assert "penalty" in lr_params

    def test_model_tuning(self, sample_classification_data):
        """Test model tuning for overfitting prevention"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = DecisionTreeClassifier(random_state=42)

        tuned_model, results = handler.tune_model(
            model, X_train, y_train, cv=3, n_iter=5  # Small numbers for fast testing
        )

        assert tuned_model is not None
        assert isinstance(results, dict)

        if "error" not in results:
            assert "best_params" in results
            assert "best_score" in results
            assert results["best_score"] is not None

    def test_apply_mitigation_regularization(self, sample_classification_data):
        """Test applying regularization mitigation"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = DecisionTreeClassifier(random_state=42)
        strategy = {
            "name": "Regularization",
            "description": "Apply regularization to reduce overfitting",
            "params": {"max_depth": 5, "min_samples_split": 10, "min_samples_leaf": 5},
        }

        mitigated_model, results = handler.apply_mitigation(
            strategy, model, X_train, y_train
        )

        assert mitigated_model is not None
        assert isinstance(results, dict)
        assert results.get("success", False) == True
        assert results["strategy"] == "Regularization"

        assert mitigated_model.max_depth == 5
        assert mitigated_model.min_samples_split == 10
        assert mitigated_model.min_samples_leaf == 5

    def test_apply_mitigation_feature_selection(self, sample_classification_data):
        """Test applying feature selection mitigation"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        strategy = {
            "name": "Feature Selection",
            "description": "Select most important features",
            "method": "feature_importance",
        }

        mitigated_model, results = handler.apply_mitigation(
            strategy, model, X_train, y_train
        )

        assert isinstance(results, dict)
        assert results["strategy"] == "Feature Selection"

        if results.get("success", False):
            assert "selector" in results
            assert "n_features_selected" in results
            assert results["n_features_selected"] <= X_train.shape[1]

    def test_apply_mitigation_ensemble(self, sample_classification_data):
        """Test applying ensemble mitigation"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = DecisionTreeClassifier(random_state=42)
        strategy = {
            "name": "Ensemble Methods",
            "description": "Use ensemble to reduce overfitting",
            "method": "ensemble",
        }

        ensemble_model, results = handler.apply_mitigation(
            strategy, model, X_train, y_train
        )

        assert isinstance(results, dict)
        assert results["strategy"] == "Ensemble Methods"

        if results.get("success", False):
            assert ensemble_model is not None
            assert "ensemble_type" in results

    def test_apply_mitigation_early_stopping(self, sample_classification_data):
        """Test applying early stopping mitigation"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        from sklearn.neural_network import MLPClassifier

        model = MLPClassifier(random_state=42, max_iter=100)

        strategy = {
            "name": "Early Stopping",
            "description": "Stop training before overfitting",
            "params": {"early_stopping": True, "validation_fraction": 0.2},
        }

        mitigated_model, results = handler.apply_mitigation(
            strategy, model, X_train, y_train
        )

        assert isinstance(results, dict)
        assert results["strategy"] == "Early Stopping"

        if not results.get("success", False):
            assert "message" in results

    def test_apply_mitigation_cross_validation(self, sample_classification_data):
        """Test applying cross-validation mitigation"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = DecisionTreeClassifier(random_state=42)
        strategy = {
            "name": "Cross-Validation",
            "description": "Use cross-validation for parameter selection",
            "method": "cv",
            "params": {"cv": 3},
        }

        tuned_model, results = handler.apply_mitigation(
            strategy, model, X_train, y_train
        )

        assert isinstance(results, dict)
        assert results["strategy"] == "Cross-Validation"

        if results.get("success", False):
            assert tuned_model is not None
            assert "best_params" in results

    def test_no_overfitting_case(self, sample_classification_data):
        """Test case where no overfitting is detected"""
        X, y = sample_classification_data
        handler = OverfittingHandler(problem_type="classification")

        train_metrics = {
            "accuracy": 0.85,
            "precision": 0.84,
            "recall": 0.86,
            "f1": 0.85,
        }

        test_metrics = {"accuracy": 0.83, "precision": 0.82, "recall": 0.84, "f1": 0.83}

        result = handler.detect_overfitting(
            train_metrics, test_metrics, "LogisticRegression"
        )

        assert result["is_overfitting"] == False
        assert result["severity"] == "None"
        assert result["overfitting_score"] < 0.1

        strategies = handler.get_mitigation_strategies("LogisticRegression", result)
        assert len(strategies) <= 1

    def test_severe_overfitting_case(self):
        """Test case with severe overfitting"""
        handler = OverfittingHandler(problem_type="classification")

        train_metrics = {"accuracy": 1.0, "precision": 1.0, "recall": 1.0, "f1": 1.0}

        test_metrics = {"accuracy": 0.6, "precision": 0.55, "recall": 0.65, "f1": 0.6}

        result = handler.detect_overfitting(train_metrics, test_metrics, "DecisionTree")

        assert result["is_overfitting"] == True
        assert result["severity"] == "Severe"
        assert result["overfitting_score"] > 0.6

        strategies = handler.get_mitigation_strategies("DecisionTree", result)
        assert len(strategies) > 0

        reg_strategy = next(
            (s for s in strategies if s["name"] == "Regularization"), None
        )
        assert reg_strategy is not None
        assert reg_strategy["priority"] == 1

    def test_error_handling(self):
        """Test error handling in overfitting handler"""
        handler = OverfittingHandler()

        invalid_strategy = {
            "name": "InvalidStrategy",
            "description": "This should fail",
        }

        model = DecisionTreeClassifier()
        X_dummy = np.array([[1, 2], [3, 4]])
        y_dummy = np.array([0, 1])

        mitigated_model, results = handler.apply_mitigation(
            invalid_strategy, model, X_dummy, y_dummy
        )

        assert mitigated_model == model
        assert results["success"] == False
        assert "message" in results or "error" in results

    def test_regression_overfitting_detection(self, sample_regression_data):
        """Test regression-specific overfitting detection"""
        X, y = sample_regression_data
        handler = OverfittingHandler(problem_type="regression")

        train_metrics = {"mse": 0.1, "rmse": 0.32, "mae": 0.25, "r2": 0.95}

        test_metrics = {"mse": 1.5, "rmse": 1.22, "mae": 1.0, "r2": 0.65}

        result = handler.detect_overfitting(
            train_metrics, test_metrics, "RandomForestRegressor"
        )

        assert "r2_gap" in result["details"]
        assert "mse_ratio" in result["details"]

        assert result["is_overfitting"] == True
        assert result["overfitting_score"] > 0.1
