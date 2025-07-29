"""
Tests for model registry functionality
"""

import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from automl.model_registry import ModelRegistry
from automl.preprocessors import StandardPreprocessor


class TestModelRegistry:
    """Test ModelRegistry functionality"""

    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = ModelRegistry()
        assert len(registry.get_models()) == 0

    def test_model_registration(self):
        """Test model registration"""
        registry = ModelRegistry()
        model = RandomForestClassifier(n_estimators=10, random_state=42)

        wrapper = registry.register("TestRF", model)

        assert "TestRF" in registry.get_models()
        assert wrapper.name == "TestRF"
        assert wrapper.model == model

    def test_model_registration_with_preprocessor(self):
        """Test model registration with preprocessor"""
        registry = ModelRegistry()
        model = LogisticRegression(random_state=42)
        preprocessor = StandardPreprocessor()

        wrapper = registry.register("TestLR", model, preprocessor)

        assert wrapper.preprocessor == preprocessor

    def test_model_unregistration(self):
        """Test model unregistration"""
        registry = ModelRegistry()
        model = RandomForestClassifier(n_estimators=10, random_state=42)

        registry.register("TestRF", model)
        assert "TestRF" in registry.get_models()

        registry.unregister("TestRF")
        assert "TestRF" not in registry.get_models()

    def test_get_specific_model(self):
        """Test getting specific model"""
        registry = ModelRegistry()
        model = RandomForestClassifier(n_estimators=10, random_state=42)

        registry.register("TestRF", model)

        wrapper = registry.get_model("TestRF")
        assert wrapper.name == "TestRF"
        assert wrapper.model == model

    def test_get_nonexistent_model(self):
        """Test getting nonexistent model"""
        registry = ModelRegistry()

        with pytest.raises(ValueError):
            registry.get_model("NonexistentModel")

    def test_multiple_models(self):
        """Test registering multiple models"""
        registry = ModelRegistry()

        models = {
            "RF": RandomForestClassifier(n_estimators=10, random_state=42),
            "LR": LogisticRegression(random_state=42),
        }

        for name, model in models.items():
            registry.register(name, model)

        registered_models = registry.get_models()
        assert len(registered_models) == 2
        assert "RF" in registered_models
        assert "LR" in registered_models

    def test_registry_clear(self):
        """Test clearing registry"""
        registry = ModelRegistry()

        registry.register("RF", RandomForestClassifier(random_state=42))
        registry.register("LR", LogisticRegression(random_state=42))

        assert len(registry.get_models()) == 2

        registry.clear()
        assert len(registry.get_models()) == 0
