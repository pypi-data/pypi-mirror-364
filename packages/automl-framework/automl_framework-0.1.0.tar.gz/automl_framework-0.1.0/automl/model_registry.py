"""
Model registry for the AutoML framework.
Manages registration and retrieval of models.
"""

import logging
from typing import Dict, Optional
from sklearn.base import BaseEstimator

from .preprocessors import Preprocessor
from .model_wrapper import ModelWrapper

logger = logging.getLogger("AutoML")


class ModelRegistry:
    """Registry for managing multiple models"""

    def __init__(self):
        self.models = {}

    def register(
        self,
        name: str,
        model_instance: BaseEstimator,
        preprocessor: Optional[Preprocessor] = None,
    ):
        """Register a model in the registry"""
        logger.info(f"Registering model: {name}")
        self.models[name] = ModelWrapper(name, model_instance, preprocessor)
        return self.models[name]

    def unregister(self, name: str):
        """Remove a model from the registry"""
        if name in self.models:
            logger.info(f"Unregistering model: {name}")
            del self.models[name]

    def get_model(self, name: str) -> ModelWrapper:
        """Get a specific model by name"""
        if name not in self.models:
            raise ValueError(f"Model {name} not found in registry")
        return self.models[name]

    def get_models(self) -> Dict[str, ModelWrapper]:
        """Get all registered models"""
        return self.models

    def clear(self):
        """Clear all models from the registry"""
        self.models = {}
        logger.info("Model registry cleared")
