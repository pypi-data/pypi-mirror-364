"""
Tests for model wrapper functionality
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from automl.model_wrapper import ModelWrapper
from automl.preprocessors import StandardPreprocessor


class TestModelWrapper:
    """Test ModelWrapper functionality"""

    def test_wrapper_initialization(self):
        """Test model wrapper initialization"""
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        assert wrapper.name == "TestRF"
        assert wrapper.model == model
        assert wrapper.preprocessor is not None
        assert not wrapper._is_fitted

    def test_wrapper_with_custom_preprocessor(self):
        """Test wrapper with custom preprocessor"""
        model = LogisticRegression(random_state=42)
        preprocessor = StandardPreprocessor()
        wrapper = ModelWrapper("TestLR", model, preprocessor)

        assert wrapper.preprocessor == preprocessor

    def test_model_fitting(self, sample_classification_data):
        """Test model fitting functionality"""
        X, y = sample_classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        wrapper.fit(X, y)

        assert wrapper._is_fitted

        log = wrapper.get_training_log()
        assert log["fit_successful"]
        assert log["training_duration"] > 0
        assert log["n_samples"] == len(X)
        assert log["n_features"] == X.shape[1]

    def test_predictions(self, sample_classification_data):
        """Test prediction functionality"""
        X, y = sample_classification_data
        X_train, X_test = X.iloc[:150], X.iloc[150:]
        y_train = y.iloc[:150]

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        wrapper.fit(X_train, y_train)
        predictions = wrapper.predict(X_test)

        assert len(predictions) == len(X_test)
        assert not np.any(np.isnan(predictions))

    def test_probability_predictions(self, sample_classification_data):
        """Test probability prediction functionality"""
        X, y = sample_classification_data
        X_train, X_test = X.iloc[:150], X.iloc[150:]
        y_train = y.iloc[:150]

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        wrapper.fit(X_train, y_train)
        probabilities = wrapper.predict_proba(X_test)

        assert len(probabilities) == len(X_test)
        assert probabilities.shape[1] >= 2
        assert np.allclose(probabilities.sum(axis=1), 1.0)

    def test_feature_importance(self, sample_classification_data):
        """Test feature importance extraction"""
        X, y = sample_classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        wrapper.fit(X, y)

        importance = wrapper.get_feature_importance()
        assert importance is not None
        assert "feature_importances" in importance
        assert len(importance["feature_importances"]) == X.shape[1]

    def test_model_saving_loading(self, sample_classification_data, temp_directory):
        """Test model saving and loading"""
        X, y = sample_classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        wrapper.fit(X, y)
        save_path = os.path.join(temp_directory, "test_model.pkl")
        wrapper.save(save_path)

        loaded_wrapper = ModelWrapper.load(save_path)

        assert loaded_wrapper.name == wrapper.name
        assert loaded_wrapper._is_fitted

        original_pred = wrapper.predict(X)
        loaded_pred = loaded_wrapper.predict(X)
        np.testing.assert_array_equal(original_pred, loaded_pred)

    def test_unfitted_model_errors(self, sample_classification_data):
        """Test errors when using unfitted model"""
        X, y = sample_classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        wrapper = ModelWrapper("TestRF", model)

        with pytest.raises(ValueError):
            wrapper.predict(X)

        with pytest.raises(ValueError):
            wrapper.predict_proba(X)

        with pytest.raises(ValueError):
            wrapper.save("dummy_path.pkl")
