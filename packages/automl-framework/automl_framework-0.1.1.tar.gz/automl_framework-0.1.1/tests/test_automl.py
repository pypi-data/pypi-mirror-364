"""
Basic tests for AutoML Framework
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.ensemble import RandomForestClassifier

from automl import AutoML, DataUtils


class TestAutoML:
    """Test AutoML main functionality"""

    def setup_method(self):
        """Set up test data"""
        X_cls, y_cls = make_classification(
            n_samples=100, n_features=10, n_classes=2, random_state=42
        )
        self.X_cls = pd.DataFrame(X_cls, columns=[f"feature_{i}" for i in range(10)])
        self.y_cls = pd.Series(y_cls)

        X_reg, y_reg = make_regression(
            n_samples=100, n_features=10, noise=0.1, random_state=42
        )
        self.X_reg = pd.DataFrame(X_reg, columns=[f"feature_{i}" for i in range(10)])
        self.y_reg = pd.Series(y_reg)

    def test_automl_initialization(self):
        """Test AutoML initialization"""
        automl = AutoML()
        assert automl.pipeline.problem_type == "classification"
        assert automl.pipeline.random_state == 42

        config = {"problem_type": "regression", "random_state": 123}
        automl = AutoML(config)
        assert automl.pipeline.problem_type == "regression"
        assert automl.pipeline.random_state == 123

    def test_model_registration(self):
        """Test model registration"""
        automl = AutoML()

        rf = RandomForestClassifier(n_estimators=10, random_state=42)
        automl.register_model("CustomRF", rf)

        models = automl.pipeline.registry.get_models()
        assert "CustomRF" in models

    def test_classification_workflow(self):
        """Test complete classification workflow"""
        automl = AutoML({"problem_type": "classification"})

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            self.X_cls, self.y_cls, test_size=0.3, random_state=42
        )

        automl.fit(X_train, y_train)

        results = automl.evaluate(X_test, y_test)
        assert len(results) > 0

        predictions = automl.predict(X_test)
        assert len(predictions) == len(y_test)

        leaderboard = automl.get_leaderboard()
        assert not leaderboard.empty

    def test_regression_workflow(self):
        """Test complete regression workflow"""
        automl = AutoML({"problem_type": "regression"})

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            self.X_reg, self.y_reg, test_size=0.3, random_state=42
        )

        automl.fit(X_train, y_train)

        results = automl.evaluate(X_test, y_test)
        assert len(results) > 0

        predictions = automl.predict(X_test)
        assert len(predictions) == len(y_test)

    def test_feature_importance(self):
        """Test feature importance extraction"""
        automl = AutoML({"problem_type": "classification"})

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            self.X_cls, self.y_cls, test_size=0.3, random_state=42
        )

        automl.fit(X_train, y_train)
        automl.evaluate(X_test, y_test)

        importance = automl.get_feature_importance()
        assert importance is not None

    def test_training_summary(self):
        """Test training summary functionality"""
        automl = AutoML({"problem_type": "classification"})

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            self.X_cls, self.y_cls, test_size=0.3, random_state=42
        )

        automl.fit(X_train, y_train)

        summary = automl.get_training_summary()
        assert "n_models_trained" in summary
        assert "successful_models" in summary
        assert "failed_models" in summary


class TestDataUtils:
    """Test DataUtils functionality"""

    def test_train_test_split(self):
        """Test data splitting"""
        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        X = pd.DataFrame(X)
        y = pd.Series(y)

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.2
        )

        assert len(X_train) == 80
        assert len(X_test) == 20
        assert len(y_train) == 80
        assert len(y_test) == 20

    def test_data_quality_check(self):
        """Test data quality checking"""
        X = pd.DataFrame(
            {
                "feature1": [1, 2, 3, 4, 5],
                "feature2": [1, 1, 1, 1, 1],
                "feature3": [1, 2, np.nan, 4, 5],
            }
        )
        y = pd.Series([0, 1, 0, 1, 0])

        report = DataUtils.check_data_quality(X, y)

        assert "missing_values_X" in report
        assert "zero_variance_features" in report
        assert "class_distribution" in report
        assert report["missing_values_X"] > 0
        assert len(report["zero_variance_features"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])
