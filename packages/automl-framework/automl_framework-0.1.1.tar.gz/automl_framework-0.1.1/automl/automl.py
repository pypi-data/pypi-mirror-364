"""
Main AutoML Class for the AutoML Framework.

Provides a simple user interface for the entire AutoML system.
"""

from typing import Dict, Optional, Any, List
from sklearn.base import BaseEstimator

from .preprocessors import Preprocessor
from .automl_pipeline import AutoMLPipeline


class AutoML:
    """Main user interface for the AutoML system"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AutoML system

        Args:
            config: Configuration dictionary with options:
                - problem_type: 'classification' or 'regression'
                - random_state: Random seed for reproducibility
                - custom_preprocessor: Custom preprocessor to use
                - custom_models: Dictionary of custom models to register
        """
        config = config or {}
        problem_type = config.get("problem_type", "classification")
        random_state = config.get("random_state", 42)

        self.pipeline = AutoMLPipeline(
            problem_type=problem_type, random_state=random_state
        )

        custom_models = config.get("custom_models", {})
        for name, model in custom_models.items():
            self.pipeline.register_model(name, model)

    def register_model(
        self,
        name: str,
        model_instance: BaseEstimator,
        preprocessor: Optional[Preprocessor] = None,
    ):
        """Register a new model"""
        return self.pipeline.register_model(name, model_instance, preprocessor)

    def unregister_model(self, name: str):
        """Remove a model from the system"""
        self.pipeline.unregister_model(name)

    def fit(self, X, y):
        """Fit all models to the data"""
        self.pipeline.fit(X, y)
        return self

    def evaluate(self, X, y):
        """Evaluate all models on test data"""
        return self.pipeline.evaluate(X, y)

    def predict(self, X):
        """Make predictions using the best model"""
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        """Get prediction probabilities from the best model (if supported)"""
        return self.pipeline.predict_proba(X)

    def get_leaderboard(self):
        """Get a leaderboard of model performance"""
        return self.pipeline.get_leaderboard()

    def save_best_model(self, path: str):
        """Save the best model to disk"""
        return self.pipeline.save_best_model(path)

    def save_all_models(self, directory: str):
        """Save all models to disk"""
        return self.pipeline.save_all_models(directory)

    def load_model(self, path: str):
        """Load a model from disk"""
        return self.pipeline.load_model(path)

    def get_model_reference(self, model_name: Optional[str] = None):
        """
        Get information about available models

        Args:
            model_name: Optional name of a specific model to get info about
                       If None, returns info for all registered models

        Returns:
            Dictionary with model information including description, strengths,
            weaknesses, and use cases
        """
        return self.pipeline.get_model_reference(model_name)

    def get_training_summary(self):
        """
        Get a summary of the overall training process

        Returns:
            Dictionary with training summary information including timing,
            successful and failed models
        """
        return self.pipeline.get_training_summary()

    def get_model_training_log(self, model_name):
        """
        Get detailed training log for a specific model

        Args:
            model_name: Name of the model to get training log for

        Returns:
            Dictionary with detailed training information for the model
        """
        return self.pipeline.get_model_training_log(model_name)

    def get_all_training_logs(self):
        """
        Get training logs for all models

        Returns:
            Dictionary mapping model names to their training logs
        """
        return self.pipeline.get_all_training_logs()

    def get_feature_importance(self, model_name=None):
        """
        Get feature importances from models

        Args:
            model_name: Optional name of a specific model to get feature importance from
                       If None, returns feature importance from the best model

        Returns:
            Dictionary with feature importance information
        """
        return self.pipeline.get_feature_importance(model_name)

    def get_fit_evaluation(self, model_name=None):
        """
        Get model fit evaluation (overfitting/underfitting assessment)

        Args:
            model_name: Optional name of a specific model to get fit evaluation for
                       If None, returns fit evaluation for the best model

        Returns:
            Dictionary with fit evaluation information including overfitting and
            underfitting scores, fit quality assessment, and train vs test metrics
        """
        return self.pipeline.get_fit_evaluation(model_name)

    def get_all_fit_evaluations(self):
        """
        Get fit evaluations for all models

        Returns:
            Dictionary mapping model names to their fit evaluations
        """
        return self.pipeline.get_all_fit_evaluations()

    def get_improvement_suggestions(self, model_name=None):
        """
        Get suggestions for improving a model

        Args:
            model_name: Optional name of a specific model to get suggestions for
                       If None, returns suggestions for the best model

        Returns:
            List of improvement suggestions based on fit evaluation
        """
        return self.pipeline.get_improvement_suggestions(model_name)
