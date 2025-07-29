"""
Model wrapper for the AutoML framework.
Provides a standardized interface for all models.
"""

import logging
import joblib
import time
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, List
from sklearn.base import BaseEstimator

from .preprocessors import Preprocessor, StandardPreprocessor

logger = logging.getLogger("AutoML")


class ModelWrapper:
    """Wrapper for machine learning models with common interface"""

    def __init__(
        self,
        name: str,
        model_instance: BaseEstimator,
        preprocessor: Optional[Preprocessor] = None,
    ):
        """
        Initialize the model wrapper

        Args:
            name: Name of the model
            model_instance: The model instance
            preprocessor: Optional preprocessor to apply before model training
        """
        self.name = name
        self.model = model_instance
        self.preprocessor = preprocessor or StandardPreprocessor()
        self._is_fitted = False

        self.training_log = {
            "start_time": None,
            "end_time": None,
            "training_duration": None,
            "n_samples": None,
            "n_features": None,
            "model_params": None,
            "preprocessor_info": None,
            "fit_successful": False,
            "error_message": None,
            "memory_usage": None,
            "warnings": [],
        }

    def fit(self, X, y):
        """Fit the model pipeline to the data"""
        import tracemalloc
        import warnings
        import gc

        tracemalloc.start()

        self.training_log["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.training_log["n_samples"] = X.shape[0]
        self.training_log["n_features"] = X.shape[1]
        self.training_log["model_params"] = str(self.model.get_params())
        self.training_log["preprocessor_info"] = type(self.preprocessor).__name__

        def warning_handler(message, category, filename, lineno, file=None, line=None):
            warning_info = {
                "message": str(message),
                "category": str(category.__name__),
                "filename": filename,
                "lineno": lineno,
            }
            self.training_log["warnings"].append(warning_info)
            original_formatwarning = warnings.formatwarning
            result = original_formatwarning(message, category, filename, lineno, line)
            return result

        original_showwarning = warnings.showwarning
        warnings.showwarning = warning_handler

        logger.info(
            f"Starting training for {self.name} with {type(self.model).__name__}"
        )
        start_time = time.time()

        try:
            gc.collect()

            logger.info(f"Preprocessing data for {self.name}...")
            X_transformed = self.preprocessor.fit_transform(X, y)

            logger.info(f"Fitting {self.name} model...")
            self.model.fit(X_transformed, y)

            self._is_fitted = True
            self.training_log["fit_successful"] = True

            current, peak = tracemalloc.get_traced_memory()
            self.training_log["memory_usage"] = {
                "current_mb": current / 1024 / 1024,
                "peak_mb": peak / 1024 / 1024,
            }

        except Exception as e:
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            logger.error(f"Error fitting {self.name}: {error_msg}\n{error_traceback}")

            self.training_log["fit_successful"] = False
            self.training_log["error_message"] = f"{error_msg}\n{error_traceback}"

            raise

        finally:
            end_time = time.time()
            training_duration = end_time - start_time

            self.training_log["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.training_log["training_duration"] = training_duration

            tracemalloc.stop()

            warnings.showwarning = original_showwarning

            if self._is_fitted:
                logger.info(
                    f"Successfully trained {self.name} in {training_duration:.2f} seconds"
                )
            else:
                logger.warning(
                    f"Failed to train {self.name} after {training_duration:.2f} seconds"
                )

        return self

    def predict(self, X):
        """Make predictions using the fitted model"""
        if not self._is_fitted:
            raise ValueError(f"Model {self.name} not fitted")

        X_transformed = self.preprocessor.transform(X)
        return self.model.predict(X_transformed)

    def predict_proba(self, X):
        """Get prediction probabilities from the model (if supported)"""
        if not self._is_fitted:
            raise ValueError(f"Model {self.name} not fitted")

        if not hasattr(self.model, "predict_proba"):
            raise ValueError(f"Model {self.name} does not support predict_proba")

        X_transformed = self.preprocessor.transform(X)
        return self.model.predict_proba(X_transformed)

    def get_training_log(self) -> Dict[str, Any]:
        """Get detailed training log information"""
        return self.training_log

    def get_feature_importance(self) -> Optional[Dict]:
        """Get feature importances if the model supports it"""
        if not self._is_fitted:
            return None

        if hasattr(self.model, "feature_importances_"):
            return {"feature_importances": self.model.feature_importances_}
        elif hasattr(self.model, "coef_"):
            return {"coefficients": self.model.coef_}
        else:
            return None

    def save(self, path: str):
        """Save the model to disk"""
        if not self._is_fitted:
            raise ValueError(f"Cannot save unfitted model {self.name}")

        model_data = {
            "model": self.model,
            "preprocessor": self.preprocessor,
            "name": self.name,
            "is_fitted": self._is_fitted,
            "training_log": self.training_log,
        }

        joblib.dump(model_data, path)
        logger.info(f"Model {self.name} saved to {path}")

    @classmethod
    def load(cls, path: str):
        """Load a model from disk"""
        model_data = joblib.load(path)

        instance = cls(
            name=model_data["name"],
            model_instance=model_data["model"],
            preprocessor=model_data["preprocessor"],
        )
        instance._is_fitted = model_data["is_fitted"]

        if "training_log" in model_data:
            instance.training_log = model_data["training_log"]

        return instance
