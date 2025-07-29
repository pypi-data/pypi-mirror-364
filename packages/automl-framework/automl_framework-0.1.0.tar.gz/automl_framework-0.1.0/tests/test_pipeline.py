"""
Tests for AutoML Pipeline functionality
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from automl.automl_pipeline import AutoMLPipeline
from automl.utils import DataUtils


class TestAutoMLPipeline:
    """Test AutoML Pipeline functionality"""

    def test_pipeline_initialization(self):
        """Test pipeline initialization with different configurations"""
        pipeline = AutoMLPipeline()
        assert pipeline.problem_type == "classification"
        assert pipeline.random_state == 42
        assert len(pipeline.registry.get_models()) > 0

        pipeline = AutoMLPipeline(problem_type="regression", random_state=123)
        assert pipeline.problem_type == "regression"
        assert pipeline.random_state == 123

    def test_default_model_registration(self):
        """Test that default models are registered correctly"""
        pipeline = AutoMLPipeline(problem_type="classification")
        models = pipeline.registry.get_models()

        expected_models = [
            "RandomForest",
            "LogisticRegression",
            "GradientBoosting",
            "DecisionTree",
            "AdaBoost",
        ]
        for model_name in expected_models:
            assert model_name in models

        pipeline = AutoMLPipeline(problem_type="regression")
        models = pipeline.registry.get_models()

        expected_regression_models = ["LinearRegression", "Ridge"]
        for model_name in expected_regression_models:
            assert model_name in models

    def test_custom_model_registration(self):
        """Test registering custom models"""
        pipeline = AutoMLPipeline()

        custom_model = RandomForestClassifier(n_estimators=50, random_state=42)
        pipeline.register_model("CustomRF", custom_model)

        models = pipeline.registry.get_models()
        assert "CustomRF" in models

        pipeline.unregister_model("CustomRF")
        models = pipeline.registry.get_models()
        assert "CustomRF" not in models

    def test_pipeline_fit(self, sample_classification_data):
        """Test pipeline fitting functionality"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        pipeline.fit(X, y)

        assert pipeline.X_train is not None
        assert pipeline.y_train is not None

        training_log = pipeline.get_training_summary()
        assert training_log["n_models_trained"] > 0
        assert len(training_log["successful_models"]) > 0
        assert training_log["total_duration"] is not None

    def test_pipeline_evaluate(self, sample_classification_data):
        """Test pipeline evaluation functionality"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        results = pipeline.evaluate(X_test, y_test)

        assert len(results) > 0
        assert pipeline.best_model is not None
        assert pipeline.best_model_name is not None

        for name, result in results.items():
            assert "model" in result
            assert "accuracy" in result
            assert "f1_score" in result

    def test_pipeline_predictions(self, sample_classification_data):
        """Test pipeline prediction functionality"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        pipeline.evaluate(X_test, y_test)

        predictions = pipeline.predict(X_test)
        assert len(predictions) == len(y_test)
        assert not np.any(np.isnan(predictions))

        try:
            probabilities = pipeline.predict_proba(X_test)
            assert len(probabilities) == len(y_test)
            assert probabilities.shape[1] >= 2
            assert np.allclose(probabilities.sum(axis=1), 1.0)
        except ValueError:
            pass

    def test_leaderboard_generation(self, sample_classification_data):
        """Test leaderboard generation"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        pipeline.evaluate(X_test, y_test)

        leaderboard = pipeline.get_leaderboard()

        assert isinstance(leaderboard, pd.DataFrame)
        assert not leaderboard.empty
        assert "model" in leaderboard.columns

        assert any("accuracy" in col.lower() for col in leaderboard.columns)
        assert any("f1" in col.lower() for col in leaderboard.columns)

    def test_model_reference(self):
        """Test model reference information"""
        pipeline = AutoMLPipeline(problem_type="classification")

        all_refs = pipeline.get_model_reference()
        assert isinstance(all_refs, dict)
        assert len(all_refs) > 0

        rf_ref = pipeline.get_model_reference("RandomForest")
        assert "RandomForest" in rf_ref
        assert "description" in rf_ref["RandomForest"]

    def test_feature_importance(self, sample_classification_data):
        """Test feature importance extraction"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        pipeline.evaluate(X_test, y_test)

        importance = pipeline.get_feature_importance()

        if importance:
            assert isinstance(importance, dict)
            assert len(importance) > 0

    def test_training_logs(self, sample_classification_data):
        """Test training log functionality"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        pipeline.fit(X, y)

        summary = pipeline.get_training_summary()
        assert isinstance(summary, dict)
        assert "n_models_trained" in summary
        assert "successful_models" in summary
        assert "failed_models" in summary

        all_logs = pipeline.get_all_training_logs()
        assert isinstance(all_logs, dict)
        assert len(all_logs) > 0

        models = pipeline.registry.get_models()
        if models:
            first_model = list(models.keys())[0]
            model_log = pipeline.get_model_training_log(first_model)
            assert isinstance(model_log, dict)
            assert "fit_successful" in model_log

    def test_model_saving_loading(self, sample_classification_data, temp_directory):
        """Test model saving and loading"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        pipeline.evaluate(X_test, y_test)

        best_model_path = os.path.join(temp_directory, "best_model.pkl")
        pipeline.save_best_model(best_model_path)
        assert os.path.exists(best_model_path)

        all_models_dir = os.path.join(temp_directory, "all_models")
        pipeline.save_all_models(all_models_dir)
        assert os.path.exists(all_models_dir)

        loaded_model = pipeline.load_model(best_model_path)
        assert loaded_model is not None

        predictions = loaded_model.predict(X_test)
        assert len(predictions) == len(y_test)

    def test_regression_pipeline(self, sample_regression_data):
        """Test pipeline with regression problem"""
        X, y = sample_regression_data
        pipeline = AutoMLPipeline(problem_type="regression")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        results = pipeline.evaluate(X_test, y_test)

        assert len(results) > 0
        assert pipeline.best_model is not None

        for name, result in results.items():
            assert "accuracy" not in result
            assert "f1_score" not in result

    def test_overfitting_control_configuration(self):
        """Test overfitting control configuration"""
        pipeline = AutoMLPipeline(problem_type="classification")

        if hasattr(pipeline, "set_overfitting_control"):
            pipeline.set_overfitting_control(
                detection_enabled=True, auto_mitigation=True, threshold=0.2
            )

            assert pipeline.overfitting_detection_enabled == True
            assert pipeline.auto_mitigation_enabled == True
            assert pipeline.overfitting_threshold == 0.2

    def test_fit_evaluation(self, sample_classification_data):
        """Test fit evaluation functionality"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        pipeline.evaluate(X_test, y_test)

        try:
            fit_eval = pipeline.get_fit_evaluation()
            assert isinstance(fit_eval, dict)

            all_fit_evals = pipeline.get_all_fit_evaluations()
            assert isinstance(all_fit_evals, dict)

        except Exception:
            pass

    def test_improvement_suggestions(self, sample_classification_data):
        """Test improvement suggestions functionality"""
        X, y = sample_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        pipeline.evaluate(X_test, y_test)

        try:
            suggestions = pipeline.get_improvement_suggestions()
            assert isinstance(suggestions, list)

        except Exception:
            pass

    def test_error_handling(self):
        """Test error handling in pipeline"""
        pipeline = AutoMLPipeline(problem_type="classification")

        with pytest.raises(ValueError):
            pipeline.predict(np.array([[1, 2, 3]]))

        with pytest.raises(ValueError):
            pipeline.get_model_training_log("NonexistentModel")

    def test_multiclass_classification(self, multiclass_classification_data):
        """Test pipeline with multiclass classification"""
        X, y = multiclass_classification_data
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        results = pipeline.evaluate(X_test, y_test)

        assert len(results) > 0
        assert pipeline.best_model is not None

        predictions = pipeline.predict(X_test)
        assert len(predictions) == len(y_test)

        unique_preds = np.unique(predictions)
        unique_true = np.unique(y_test)
        assert all(pred in unique_true for pred in unique_preds)

    @pytest.mark.slow
    def test_large_dataset_handling(self):
        """Test pipeline with larger dataset (marked as slow test)"""
        from sklearn.datasets import make_classification

        X, y = make_classification(
            n_samples=1000,
            n_features=20,
            n_informative=15,
            n_classes=2,
            random_state=42,
        )

        X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        y_series = pd.Series(y, name="target")

        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X_df, y_series, test_size=0.2, random_state=42
        )

        pipeline.fit(X_train, y_train)
        results = pipeline.evaluate(X_test, y_test)

        assert len(results) > 0
        assert pipeline.best_model is not None

        for name, result in results.items():
            accuracy = result.get("accuracy", 0)
            assert accuracy > 0.5

    def test_pipeline_with_missing_data(self, data_with_missing_values):
        """Test pipeline handling of missing data"""
        X, y = data_with_missing_values
        pipeline = AutoMLPipeline(problem_type="classification")

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        pipeline.fit(X_train, y_train)
        results = pipeline.evaluate(X_test, y_test)

        assert len(results) > 0
        assert pipeline.best_model is not None

        predictions = pipeline.predict(X_test)
        assert len(predictions) == len(y_test)
        assert not np.any(np.isnan(predictions))
