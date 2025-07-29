"""
Core AutoML pipeline for the AutoML framework.
Manages the entire workflow of model training and evaluation.
"""

import os
import logging
import pandas as pd
import time
import traceback
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime
import numpy as np

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    ExtraTreesClassifier,
    BaggingClassifier,
)
from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier
from sklearn.base import BaseEstimator, clone
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neural_network import MLPClassifier

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

from .preprocessors import Preprocessor
from .model_registry import ModelRegistry
from .model_wrapper import ModelWrapper
from .metrics import MetricsCalculator
from .model_evaluation import ModelEvaluator
from overfitting_handler import OverfittingHandler

logger = logging.getLogger("AutoML")

CLASSIFICATION_MODEL_REFERENCE = {
    "RandomForest": {
        "description": "An ensemble learning method using multiple decision trees",
        "strengths": "Handles high-dimensional data well, robust to overfitting, good for imbalanced data",
        "weaknesses": "Can be computationally intensive, black-box model with limited interpretability",
        "use_cases": "General classification tasks, feature importance analysis",
        "overfitting_risk": "Medium",
        "mitigation_strategies": [
            "max_depth",
            "min_samples_split",
            "min_samples_leaf",
            "max_features",
        ],
    },
    "LogisticRegression": {
        "description": "A linear model for classification using the logistic function",
        "strengths": "Simple, interpretable, works well for linearly separable data, provides probability estimates",
        "weaknesses": "Limited to linear decision boundaries, sensitive to outliers",
        "use_cases": "Binary classification, when interpretability is important, baseline model",
        "overfitting_risk": "Low",
        "mitigation_strategies": ["C", "penalty"],
    },
    "GradientBoosting": {
        "description": "An ensemble technique that builds trees sequentially to correct errors",
        "strengths": "Often provides best accuracy, handles different types of data well",
        "weaknesses": "Can overfit on noisy data, slower to train than random forests",
        "use_cases": "When predictive performance is the priority",
        "overfitting_risk": "High",
        "mitigation_strategies": [
            "learning_rate",
            "max_depth",
            "min_samples_split",
            "n_estimators",
            "subsample",
        ],
    },
    "DecisionTree": {
        "description": "A tree-like model making decisions based on feature values",
        "strengths": "Highly interpretable, handles both numerical and categorical data",
        "weaknesses": "Prone to overfitting, unstable (small changes in data can lead to different trees)",
        "use_cases": "When interpretability is important, rule extraction",
        "overfitting_risk": "Very High",
        "mitigation_strategies": [
            "max_depth",
            "min_samples_split",
            "min_samples_leaf",
            "ccp_alpha",
        ],
    },
    "AdaBoost": {
        "description": "An ensemble method that combines weak learners sequentially",
        "strengths": "Simple to implement, not prone to overfitting",
        "weaknesses": "Sensitive to noisy data and outliers",
        "use_cases": "Face detection, general classification tasks",
        "overfitting_risk": "Medium",
        "mitigation_strategies": ["learning_rate", "n_estimators"],
    },
}

REGRESSION_MODEL_REFERENCE = {
    "LinearRegression": {
        "description": "A linear approach to modelling relationships between variables",
        "strengths": "Simple, interpretable, fast",
        "weaknesses": "Limited to linear relationships, sensitive to outliers",
        "use_cases": "Simple predictive tasks with linear relationships",
        "overfitting_risk": "Low",
        "mitigation_strategies": [],
    },
    "Ridge": {
        "description": "Linear regression with L2 regularization",
        "strengths": "Handles multicollinearity well, reduces overfitting",
        "weaknesses": "Still assumes linear relationship",
        "use_cases": "When features are correlated, prevents overfitting",
        "overfitting_risk": "Low",
        "mitigation_strategies": ["alpha"],
    },
}


class AutoMLPipeline:
    """Core AutoML pipeline that manages model training and evaluation"""

    def __init__(self, problem_type: str = "classification", random_state: int = 42):
        """
        Initialize the AutoML pipeline

        Args:
            problem_type: Type of problem ('classification' or 'regression')
            random_state: Random seed for reproducibility
        """
        self.problem_type = problem_type
        self.random_state = random_state
        self.registry = ModelRegistry()
        self.metrics_calculator = MetricsCalculator(problem_type)
        self.model_evaluator = ModelEvaluator(problem_type)
        self.overfitting_handler = OverfittingHandler(problem_type)

        self.results = {}
        self.best_model = None
        self.best_model_name = None
        self.model_reference = (
            CLASSIFICATION_MODEL_REFERENCE
            if problem_type == "classification"
            else REGRESSION_MODEL_REFERENCE
        )

        self.X_train = None
        self.y_train = None

        self.overfitting_detection_enabled = True
        self.auto_mitigation_enabled = True
        self.overfitting_threshold = 0.3

        self.mitigated_models = {}

        self.training_log = {
            "start_time": None,
            "end_time": None,
            "total_duration": None,
            "n_models_trained": 0,
            "successful_models": [],
            "failed_models": [],
            "mitigated_models": [],
            "overfitting_detected": [],
            "data_info": {
                "n_samples": None,
                "n_features": None,
                "class_distribution": None,
            },
        }

        self._register_default_models()

    def _register_default_models(self):
        """Register default models based on problem type with references"""
        if self.problem_type == "classification":
            self.registry.register(
                "RandomForest",
                RandomForestClassifier(
                    n_estimators=100, random_state=self.random_state
                ),
            )
            self.registry.register(
                "LogisticRegression",
                LogisticRegression(
                    C=1.0,
                    penalty="l2",
                    solver="liblinear",
                    random_state=self.random_state,
                    max_iter=1000,
                ),
            )
            self.registry.register(
                "GradientBoosting",
                GradientBoostingClassifier(
                    n_estimators=100, learning_rate=0.1, random_state=self.random_state
                ),
            )
            self.registry.register(
                "DecisionTree",
                DecisionTreeClassifier(max_depth=None, random_state=self.random_state),
            )
            self.registry.register(
                "AdaBoost",
                AdaBoostClassifier(
                    n_estimators=50, learning_rate=1.0, random_state=self.random_state
                ),
            )
        elif self.problem_type == "regression":
            self.registry.register("LinearRegression", LinearRegression())
            self.registry.register(
                "Ridge", Ridge(alpha=1.0, random_state=self.random_state)
            )
        else:
            logger.warning(
                f"No default models registered for problem type: {self.problem_type}"
            )

    def set_overfitting_control(
        self,
        detection_enabled: bool = True,
        auto_mitigation: bool = True,
        threshold: float = 0.3,
    ):
        """
        Configure overfitting detection and mitigation settings

        Args:
            detection_enabled: Whether to enable overfitting detection
            auto_mitigation: Whether to automatically apply mitigation strategies
            threshold: Overfitting score threshold for automatic mitigation
        """
        self.overfitting_detection_enabled = detection_enabled
        self.auto_mitigation_enabled = auto_mitigation
        self.overfitting_threshold = threshold

        logger.info(
            f"Overfitting control: detection={'enabled' if detection_enabled else 'disabled'}, "
            f"auto_mitigation={'enabled' if auto_mitigation else 'disabled'}, "
            f"threshold={threshold}"
        )

    def register_model(
        self,
        name: str,
        model_instance: BaseEstimator,
        preprocessor: Optional[Preprocessor] = None,
    ):
        """Register a new model in the pipeline"""
        return self.registry.register(name, model_instance, preprocessor)

    def unregister_model(self, name: str):
        """Remove a model from the pipeline"""
        self.registry.unregister(name)

    def fit(self, X, y):
        """Fit all registered models to the data"""
        self.X_train = X
        self.y_train = y

        self.training_log["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.training_log["data_info"]["n_samples"] = X.shape[0]
        self.training_log["data_info"]["n_features"] = X.shape[1]

        if self.problem_type == "classification":
            import pandas as pd
            import numpy as np

            value_counts = pd.Series(y).value_counts(normalize=True).to_dict()
            self.training_log["data_info"]["class_distribution"] = value_counts

        models = self.registry.get_models()
        logger.info(f"Fitting {len(models)} models...")

        pipeline_start_time = time.time()

        if len(models) == 0:
            logger.warning("No models registered. Register models before fitting.")
            return self

        successful_models = []
        failed_models = []

        for name, model in models.items():
            logger.info(f"Training {name}...")
            try:
                model.fit(X, y)

                training_log = model.get_training_log()
                if training_log["fit_successful"]:
                    successful_models.append(name)
                else:
                    failed_models.append(
                        {
                            "name": name,
                            "error": training_log.get("error_message", "Unknown error"),
                        }
                    )

            except Exception as e:
                logger.error(f"Error fitting model {name}: {str(e)}")
                failed_models.append({"name": name, "error": str(e)})

        pipeline_end_time = time.time()
        self.training_log["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.training_log["total_duration"] = pipeline_end_time - pipeline_start_time
        self.training_log["n_models_trained"] = len(models)
        self.training_log["successful_models"] = successful_models
        self.training_log["failed_models"] = failed_models

        logger.info(
            f"Completed training {len(successful_models)} models successfully. "
            + f"{len(failed_models)} models failed."
        )

        return self

    def evaluate(self, X, y):
        """Evaluate all fitted models and handle overfitting"""
        self.X_test = X
        self.y_test = y

        models = self.registry.get_models()
        logger.info(f"Evaluating {len(models)} models...")

        if len(models) == 0:
            logger.warning("No models registered. Register models before evaluation.")
            return {}

        overfitting_models = []

        for name, model in models.items():
            try:
                y_pred = model.predict(X)

                y_pred_proba = None
                try:
                    y_pred_proba = model.predict_proba(X)
                except Exception as e:
                    logging.error(f"An error occurred: {e}")

                metrics = self.metrics_calculator.calculate_metrics(
                    y, y_pred, y_pred_proba
                )

                if self.problem_type == "classification":
                    logger.info(
                        f"""\nClassification Report for {name}:\n{
                            self.metrics_calculator.get_classification_report(y, y_pred)
                            }"""
                    )

                feature_importance = model.get_feature_importance()

                fit_evaluation = {}
                if self.X_train is not None and self.y_train is not None:
                    try:
                        fit_evaluation = self.model_evaluator.evaluate_model_fit(
                            model=model,
                            X_train=self.X_train,
                            y_train=self.y_train,
                            X_test=X,
                            y_test=y,
                        )

                        try:
                            fit_evaluation["improvement_suggestions"] = (
                                self.model_evaluator.get_improvement_suggestions(
                                    fit_evaluation
                                )
                            )
                        except Exception as e:
                            logger.error(
                                f"Error getting improvement suggestions for {name}: {str(e)}"
                            )
                            fit_evaluation["improvement_suggestions"] = [
                                "Could not generate suggestions due to an error."
                            ]

                        logger.info(f"\nModel Fit Evaluation for {name}:")
                        logger.info(
                            f"Fit Quality: {fit_evaluation.get('fit_quality', 'Unknown')}"
                        )
                        logger.info(
                            f"Overfitting Score: {fit_evaluation.get('overfitting_score', 0):.2f}"
                        )
                        logger.info(
                            f"Underfitting Score: {fit_evaluation.get('underfitting_score', 0):.2f}"
                        )
                    except Exception as e:
                        logger.error(f"Error evaluating fit for model {name}: {str(e)}")
                        fit_evaluation = {
                            "fit_quality": "Unknown (error)",
                            "overfitting_score": 0,
                            "underfitting_score": 0,
                        }

                self.results[name] = {
                    "model": model,
                    "training_log": model.get_training_log(),
                    "feature_importance": feature_importance,
                    "fit_evaluation": fit_evaluation,
                    **metrics,
                }

                if self.overfitting_detection_enabled:
                    train_metrics = self._get_training_metrics(model)
                    test_metrics = self._get_test_metrics(metrics)

                    overfitting_result = self.overfitting_handler.detect_overfitting(
                        train_metrics, test_metrics, name
                    )

                    self.results[name]["overfitting_assessment"] = overfitting_result

                    if overfitting_result.get("is_overfitting", False):
                        overfitting_models.append(
                            {
                                "name": name,
                                "score": overfitting_result.get("overfitting_score", 0),
                                "severity": overfitting_result.get(
                                    "severity", "Unknown"
                                ),
                            }
                        )

                        logger.warning(
                            f"Overfitting detected in {name}: "
                            f"Score={overfitting_result.get('overfitting_score', 0):.2f}, "
                            f"Severity={overfitting_result.get('severity', 'Unknown')}"
                        )

                        self.training_log["overfitting_detected"].append(name)

                        if (
                            self.auto_mitigation_enabled
                            and overfitting_result.get("overfitting_score", 0)
                            >= self.overfitting_threshold
                        ):
                            self._apply_overfitting_mitigation(
                                name, model, overfitting_result
                            )

            except Exception as e:
                logger.error(f"Error evaluating model {name}: {str(e)}")
                logger.error(traceback.format_exc())

        if self.results:
            metric_to_optimize = (
                "f1_score" if self.problem_type == "classification" else "r2"
            )

            all_models = {**self.results}

            best_name = max(
                all_models, key=lambda x: all_models[x].get(metric_to_optimize, 0)
            )

            if best_name in self.mitigated_models:
                self.best_model = self.mitigated_models[best_name]["model"]
                self.best_model_name = f"{best_name}_mitigated"
                logger.info(
                    f"""Best model: {self.best_model_name} with {metric_to_optimize}:
                    {all_models[best_name].get(metric_to_optimize, 0):.4f}"""
                )
            else:
                self.best_model = self.results[best_name]["model"]
                self.best_model_name = best_name
                logger.info(
                    f"""Best model: {best_name} with {metric_to_optimize}:
                    {self.results[best_name].get(metric_to_optimize, 0):.4f}"""
                )

        return self.results

    def _get_training_metrics(self, model):
        """Get training metrics for a model"""
        y_train_pred = model.predict(self.X_train)

        if self.problem_type == "classification":
            from sklearn.metrics import (
                accuracy_score,
                precision_score,
                recall_score,
                f1_score,
            )

            return {
                "accuracy": accuracy_score(self.y_train, y_train_pred),
                "precision": precision_score(
                    self.y_train, y_train_pred, average="weighted"
                ),
                "recall": recall_score(self.y_train, y_train_pred, average="weighted"),
                "f1": f1_score(self.y_train, y_train_pred, average="weighted"),
            }
        else:
            from sklearn.metrics import (
                mean_squared_error,
                r2_score,
                mean_absolute_error,
            )

            return {
                "mse": mean_squared_error(self.y_train, y_train_pred),
                "rmse": np.sqrt(mean_squared_error(self.y_train, y_train_pred)),
                "mae": mean_absolute_error(self.y_train, y_train_pred),
                "r2": r2_score(self.y_train, y_train_pred),
            }

    def _get_test_metrics(self, metrics):
        """Extract test metrics from metrics dictionary"""
        if self.problem_type == "classification":
            return {
                "accuracy": metrics.get("accuracy", 0),
                "precision": metrics.get("precision", 0),
                "recall": metrics.get("recall", 0),
                "f1": metrics.get("f1_score", 0),
            }
        else:
            return {
                "mse": metrics.get("mse", 0),
                "rmse": metrics.get("rmse", 0),
                "mae": metrics.get("mae", 0),
                "r2": metrics.get("r2", 0),
            }

    def _apply_overfitting_mitigation(self, model_name, model, overfitting_assessment):
        """Apply overfitting mitigation strategies to a model"""
        logger.info(f"Applying automatic overfitting mitigation for {model_name}")

        strategies = self.overfitting_handler.get_mitigation_strategies(
            model_name, overfitting_assessment
        )

        if not strategies:
            logger.warning(f"No mitigation strategies available for {model_name}")
            return

        strategy = strategies[0]

        mitigated_model, results = self.overfitting_handler.apply_mitigation(
            model.model, strategy, self.X_train, self.y_train
        )

        if results.get("success", False):
            from copy import deepcopy

            new_wrapper = ModelWrapper(
                f"{model_name}_mitigated", mitigated_model, deepcopy(model.preprocessor)
            )

            new_wrapper.fit(self.X_train, self.y_train)

            self.mitigated_models[model_name] = {
                "model": new_wrapper,
                "strategy": strategy.get("name"),
                "original_model": model,
                "results": results,
            }

            self.training_log["mitigated_models"].append(model_name)

            logger.info(
                f"Successfully mitigated overfitting in {model_name} using {strategy.get('name')} strategy"
            )
        else:
            logger.warning(
                f"Failed to mitigate overfitting in {model_name}: {results.get('message', 'Unknown error')}"
            )

    def get_model_reference(self, model_name: Optional[str] = None) -> Dict:
        """
        Get information about registered models

        Args:
            model_name: Optional name of a specific model to get info about
                       If None, returns info for all registered models

        Returns:
            Dictionary with model information
        """
        if model_name is not None:
            if model_name in self.model_reference:
                return {model_name: self.model_reference[model_name]}
            else:
                return {model_name: {"description": "Custom or unknown model"}}
        else:
            registered_models = self.registry.get_models().keys()
            return {
                name: self.model_reference.get(
                    name, {"description": "Custom or unknown model"}
                )
                for name in registered_models
            }

    def predict(self, X):
        """Make predictions using the best model"""
        if self.best_model is None:
            raise ValueError(
                "No best model available. Call fit() and evaluate() first."
            )
        return self.best_model.predict(X)

    def predict_proba(self, X):
        """Get prediction probabilities from the best model (if supported)"""
        if self.best_model is None:
            raise ValueError(
                "No best model available. Call fit() and evaluate() first."
            )
        return self.best_model.predict_proba(X)

    def get_leaderboard(self) -> pd.DataFrame:
        """
        Get a comprehensive leaderboard of model performance with train-test gaps

        Returns:
            DataFrame with model performance metrics including train, test, and gap values
        """
        if not self.results:
            raise ValueError("No results available. Call evaluate() first.")

        data = []

        def safe_scalar(x):
            if x is None:
                return 0.0
            if (
                hasattr(x, "shape")
                and len(getattr(x, "shape", [])) > 0
                and x.shape[0] > 1
            ):
                return float(np.mean(x))
            if hasattr(x, "__len__") and not isinstance(x, (str, dict)) and len(x) > 1:
                return float(np.mean(x))
            try:
                return float(x)
            except (TypeError, ValueError):
                return 0.0

        for name, result in self.results.items():
            row = {
                "model": name,
                "training_time": (
                    result["training_log"]["training_duration"]
                    if "training_log" in result
                    else None
                ),
            }

            if "fit_evaluation" in result and "fit_quality" in result["fit_evaluation"]:
                row["fit_quality"] = result["fit_evaluation"]["fit_quality"]
                row["overfitting_score"] = safe_scalar(
                    result["fit_evaluation"].get("overfitting_score", 0)
                )
                row["underfitting_score"] = safe_scalar(
                    result["fit_evaluation"].get("underfitting_score", 0)
                )

            if "overfitting_assessment" in result:
                row["overfitting_severity"] = result["overfitting_assessment"].get(
                    "severity", "None"
                )

            if self.problem_type == "classification":
                if "train_accuracy" in result.get(
                    "fit_evaluation", {}
                ) and "test_accuracy" in result.get("fit_evaluation", {}):
                    row["train_accuracy"] = safe_scalar(
                        result["fit_evaluation"]["train_accuracy"]
                    )
                    row["test_accuracy"] = safe_scalar(
                        result["fit_evaluation"]["test_accuracy"]
                    )
                    row["accuracy_gap"] = safe_scalar(
                        row["train_accuracy"] - row["test_accuracy"]
                    )
                else:
                    row["train_accuracy"] = None
                    row["test_accuracy"] = safe_scalar(result.get("accuracy", None))
                    row["accuracy_gap"] = None

                if "train_precision" in result.get(
                    "fit_evaluation", {}
                ) and "test_precision" in result.get("fit_evaluation", {}):
                    row["train_precision"] = safe_scalar(
                        result["fit_evaluation"]["train_precision"]
                    )
                    row["test_precision"] = safe_scalar(
                        result["fit_evaluation"]["test_precision"]
                    )
                    row["precision_gap"] = safe_scalar(
                        row["train_precision"] - row["test_precision"]
                    )
                else:
                    row["train_precision"] = None
                    row["test_precision"] = safe_scalar(result.get("precision", None))
                    row["precision_gap"] = None

                if "train_recall" in result.get(
                    "fit_evaluation", {}
                ) and "test_recall" in result.get("fit_evaluation", {}):
                    row["train_recall"] = safe_scalar(
                        result["fit_evaluation"]["train_recall"]
                    )
                    row["test_recall"] = safe_scalar(
                        result["fit_evaluation"]["test_recall"]
                    )
                    row["recall_gap"] = safe_scalar(
                        row["train_recall"] - row["test_recall"]
                    )
                else:
                    row["train_recall"] = None
                    row["test_recall"] = safe_scalar(result.get("recall", None))
                    row["recall_gap"] = None

                if "train_f1" in result.get(
                    "fit_evaluation", {}
                ) and "test_f1" in result.get("fit_evaluation", {}):
                    row["train_f1"] = safe_scalar(result["fit_evaluation"]["train_f1"])
                    row["test_f1"] = safe_scalar(result["fit_evaluation"]["test_f1"])
                    row["f1_gap"] = safe_scalar(row["train_f1"] - row["test_f1"])
                else:
                    row["train_f1"] = None
                    row["test_f1"] = safe_scalar(result.get("f1_score", None))
                    row["f1_gap"] = None

                if "roc_auc" in result:
                    row["roc_auc"] = safe_scalar(result["roc_auc"])

            else:
                if "train_r2" in result.get(
                    "fit_evaluation", {}
                ) and "test_r2" in result.get("fit_evaluation", {}):
                    row["train_r2"] = safe_scalar(result["fit_evaluation"]["train_r2"])
                    row["test_r2"] = safe_scalar(result["fit_evaluation"]["test_r2"])
                    row["r2_gap"] = safe_scalar(row["train_r2"] - row["test_r2"])
                else:
                    row["train_r2"] = None
                    row["test_r2"] = safe_scalar(result.get("r2", None))
                    row["r2_gap"] = None

                if "train_mse" in result.get(
                    "fit_evaluation", {}
                ) and "test_mse" in result.get("fit_evaluation", {}):
                    row["train_mse"] = safe_scalar(
                        result["fit_evaluation"]["train_mse"]
                    )
                    row["test_mse"] = safe_scalar(result["fit_evaluation"]["test_mse"])
                    if row["train_mse"] and row["train_mse"] > 0:
                        row["mse_ratio"] = safe_scalar(
                            row["test_mse"] / row["train_mse"]
                        )
                    else:
                        row["mse_ratio"] = None
                else:
                    row["train_mse"] = None
                    row["test_mse"] = safe_scalar(result.get("mse", None))
                    row["mse_ratio"] = None

            data.append(row)

        for name, result in self.mitigated_models.items():
            mitigated_metrics = self._evaluate_single_model(result["model"], name)

            row = {
                "model": f"{name}_mitigated",
                "training_time": result["model"]
                .get_training_log()
                .get("training_duration", None),
                "fit_quality": "Mitigated",
                "mitigation_strategy": result["strategy"],
            }

            if self.problem_type == "classification":
                row["test_accuracy"] = safe_scalar(
                    mitigated_metrics.get("accuracy", None)
                )
                row["test_precision"] = safe_scalar(
                    mitigated_metrics.get("precision", None)
                )
                row["test_recall"] = safe_scalar(mitigated_metrics.get("recall", None))
                row["test_f1"] = safe_scalar(mitigated_metrics.get("f1_score", None))
                if "roc_auc" in mitigated_metrics:
                    row["roc_auc"] = safe_scalar(mitigated_metrics["roc_auc"])
            else:
                row["test_r2"] = safe_scalar(mitigated_metrics.get("r2", None))
                row["test_mse"] = safe_scalar(mitigated_metrics.get("mse", None))

            data.append(row)

        df = pd.DataFrame(data)

        if df.empty:
            return df

        if self.problem_type == "classification":
            columns = [
                "model",
                "training_time",
                "fit_quality",
                "overfitting_score",
                "underfitting_score",
                "overfitting_severity",
                "train_accuracy",
                "test_accuracy",
                "accuracy_gap",
                "train_precision",
                "test_precision",
                "precision_gap",
                "train_recall",
                "test_recall",
                "recall_gap",
                "train_f1",
                "test_f1",
                "f1_gap",
                "roc_auc",
            ]

            columns = [col for col in columns if col in df.columns]

            other_cols = [col for col in df.columns if col not in columns]
            columns.extend(other_cols)

            df = df[columns]
            sort_by = (
                "test_f1"
                if "test_f1" in df.columns
                else "f1_score" if "f1_score" in df.columns else "test_accuracy"
            )

        else:
            columns = [
                "model",
                "training_time",
                "fit_quality",
                "overfitting_score",
                "underfitting_score",
                "overfitting_severity",
                "train_r2",
                "test_r2",
                "r2_gap",
                "train_mse",
                "test_mse",
                "mse_ratio",
            ]

            columns = [col for col in columns if col in df.columns]

            other_cols = [col for col in df.columns if col not in columns]
            columns.extend(other_cols)

            df = df[columns]
            sort_by = "test_r2" if "test_r2" in df.columns else "r2"

        ascending = True if (sort_by == "mse" or sort_by == "test_mse") else False

        try:
            if sort_by in df.columns:
                df[sort_by] = df[sort_by].apply(lambda x: safe_scalar(x))
                df = df.sort_values(sort_by, ascending=ascending)
        except Exception as e:
            import logging

            logger = logging.getLogger("AutoML")
            logger.warning(f"Error sorting leaderboard: {str(e)}")

        return df

    def _evaluate_single_model(self, model, name):
        """Evaluate a single model on test data"""
        if (
            not hasattr(self, "X_test")
            or self.X_test is None
            or not hasattr(self, "y_test")
            or self.y_test is None
        ):
            logger.error(f"Cannot evaluate model {name}: No test data available")
            return {}

        try:
            y_pred = model.predict(self.X_test)

            metrics = self.metrics_calculator.calculate_metrics(self.y_test, y_pred)

            return metrics
        except Exception as e:
            logger.error(f"Error evaluating model {name}: {str(e)}")
            return {}

    def get_training_summary(self) -> Dict:
        """Get a summary of the training process"""
        return self.training_log

    def get_model_training_log(self, model_name: str) -> Dict:
        """Get detailed training log for a specific model"""
        if model_name not in self.registry.get_models():
            raise ValueError(f"Model {model_name} not found in registry")

        model = self.registry.get_model(model_name)
        return model.get_training_log()

    def get_all_training_logs(self) -> Dict[str, Dict]:
        """Get training logs for all models"""
        models = self.registry.get_models()
        return {name: model.get_training_log() for name, model in models.items()}

    def get_feature_importance(self, model_name: Optional[str] = None) -> Dict:
        """
        Get feature importances from models

        Args:
            model_name: Optional name of a specific model to get feature importance from
                       If None, returns feature importance from the best model

        Returns:
            Dictionary with feature importance information
        """
        if model_name is not None:
            if model_name in self.registry.get_models():
                model = self.registry.get_model(model_name)
                return model.get_feature_importance() or {}
            else:
                raise ValueError(f"Model {model_name} not found in registry")
        else:
            if self.best_model is None:
                raise ValueError(
                    "No best model available. Call fit() and evaluate() first."
                )

            return self.best_model.get_feature_importance() or {}

    def get_fit_evaluation(self, model_name: Optional[str] = None) -> Dict:
        """
        Get model fit evaluation (overfitting/underfitting assessment)

        Args:
            model_name: Optional name of a specific model to get fit evaluation for
                       If None, returns fit evaluation for the best model

        Returns:
            Dictionary with fit evaluation information
        """
        if not self.results:
            raise ValueError("No evaluation results available. Call evaluate() first.")

        if model_name is not None:
            if model_name not in self.results:
                raise ValueError(f"Model {model_name} not found in results")

            return self.results[model_name].get("fit_evaluation", {})
        else:
            if self.best_model_name is None:
                raise ValueError(
                    "No best model available. Call fit() and evaluate() first."
                )

            return self.results[self.best_model_name.split("_")[0]].get(
                "fit_evaluation", {}
            )

    def get_all_fit_evaluations(self) -> Dict[str, Dict]:
        """
        Get fit evaluations for all models

        Returns:
            Dictionary mapping model names to their fit evaluations
        """
        if not self.results:
            raise ValueError("No evaluation results available. Call evaluate() first.")

        return {
            name: result.get("fit_evaluation", {})
            for name, result in self.results.items()
        }

    def get_overfitting_assessment(self, model_name: Optional[str] = None) -> Dict:
        """
        Get overfitting assessment for a model

        Args:
            model_name: Optional name of a specific model
                       If None, returns assessment for the best model

        Returns:
            Dictionary with overfitting assessment
        """
        if not self.results:
            raise ValueError("No evaluation results available. Call evaluate() first.")

        if model_name is not None:
            if model_name not in self.results:
                raise ValueError(f"Model {model_name} not found in results")

            return self.results[model_name].get("overfitting_assessment", {})
        else:
            if self.best_model_name is None:
                raise ValueError(
                    "No best model available. Call fit() and evaluate() first."
                )

            base_name = self.best_model_name.split("_")[0]
            return self.results[base_name].get("overfitting_assessment", {})

    def get_all_overfitting_assessments(self) -> Dict[str, Dict]:
        """
        Get overfitting assessments for all models

        Returns:
            Dictionary mapping model names to their overfitting assessments
        """
        if not self.results:
            raise ValueError("No evaluation results available. Call evaluate() first.")

        return {
            name: result.get("overfitting_assessment", {})
            for name, result in self.results.items()
        }

    def get_mitigation_strategies(self, model_name: str) -> List[Dict]:
        """
        Get available overfitting mitigation strategies for a model

        Args:
            model_name: Name of the model

        Returns:
            List of strategies with descriptions
        """
        if not self.results or model_name not in self.results:
            raise ValueError(f"Model {model_name} not found in results")

        overfitting_assessment = self.results[model_name].get(
            "overfitting_assessment", {}
        )

        return self.overfitting_handler.get_mitigation_strategies(
            model_name, overfitting_assessment
        )

    def get_mitigated_models(self) -> Dict[str, Dict]:
        """
        Get information about mitigated models

        Returns:
            Dictionary with mitigated model information
        """
        return {
            name: {
                "strategy": result["strategy"],
                "original_model": result["original_model"].name,
            }
            for name, result in self.mitigated_models.items()
        }

    def manually_mitigate_overfitting(
        self, model_name: str, strategy_name: str
    ) -> Dict:
        """
        Manually apply a specific mitigation strategy to a model

        Args:
            model_name: Name of the model to mitigate
            strategy_name: Name of the strategy to apply

        Returns:
            Dictionary with results
        """
        if not self.results or model_name not in self.results:
            raise ValueError(f"Model {model_name} not found in results")

        model = self.registry.get_model(model_name)

        overfitting_assessment = self.results[model_name].get(
            "overfitting_assessment", {}
        )

        strategies = self.overfitting_handler.get_mitigation_strategies(
            model_name, overfitting_assessment
        )

        strategy = next((s for s in strategies if s["name"] == strategy_name), None)

        if not strategy:
            available_strategies = [s["name"] for s in strategies]
            raise ValueError(
                f"Strategy '{strategy_name}' not found. Available strategies: {available_strategies}"
            )

        mitigated_model, results = self.overfitting_handler.apply_mitigation(
            model.model, strategy, self.X_train, self.y_train
        )

        if results.get("success", False):
            from copy import deepcopy

            new_wrapper = ModelWrapper(
                f"{model_name}_mitigated_{strategy_name.lower().replace(' ', '_')}",
                mitigated_model,
                deepcopy(model.preprocessor),
            )

            new_wrapper.fit(self.X_train, self.y_train)

            self.mitigated_models[f"{model_name}_{strategy_name}"] = {
                "model": new_wrapper,
                "strategy": strategy_name,
                "original_model": model,
                "results": results,
            }

            self.training_log["mitigated_models"].append(
                f"{model_name}_{strategy_name}"
            )

            logger.info(
                f"Successfully mitigated overfitting in {model_name} using {strategy_name} strategy"
            )

            return {
                "success": True,
                "model_name": f"{model_name}_mitigated_{strategy_name.lower().replace(' ', '_')}",
                "strategy": strategy_name,
                "details": results,
            }
        else:
            logger.warning(
                f"""Failed to mitigate overfitting in {model_name} using {strategy_name}:
                {results.get('message', 'Unknown error')}"""
            )

            return {
                "success": False,
                "error": results.get("message", "Unknown error"),
                "details": results,
            }

    def get_improvement_suggestions(
        self, model_name: Optional[str] = None
    ) -> List[str]:
        """
        Get suggestions for improving a model

        Args:
            model_name: Optional name of a specific model to get suggestions for
                       If None, returns suggestions for the best model

        Returns:
            List of improvement suggestions based on fit evaluation
        """
        fit_evaluation = self.get_fit_evaluation(model_name)

        basic_suggestions = fit_evaluation.get("improvement_suggestions", [])

        if model_name is None:
            model_name = (
                self.best_model_name.split("_")[0] if self.best_model_name else None
            )

        if model_name and model_name in self.results:
            overfitting_assessment = self.results[model_name].get(
                "overfitting_assessment", {}
            )

            if overfitting_assessment.get("is_overfitting", False):
                strategies = self.overfitting_handler.get_mitigation_strategies(
                    model_name, overfitting_assessment
                )

                mitigation_suggestions = [
                    f"{strategy['name']}: {strategy['description']}"
                    for strategy in strategies[:3]
                ]

                all_suggestions = (
                    basic_suggestions
                    + ["\nOverfitting Mitigation Strategies:"]
                    + mitigation_suggestions
                )
                return all_suggestions

        return basic_suggestions

    def save_best_model(self, path: str):
        """Save the best model to disk"""
        if self.best_model is None:
            raise ValueError("No best model available")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.best_model.save(path)
        logger.info(f"Best model ({self.best_model_name}) saved to {path}")

    def save_all_models(self, directory: str):
        """Save all models to disk"""
        if not self.results:
            raise ValueError("No models evaluated yet")

        os.makedirs(directory, exist_ok=True)

        for name, result in self.results.items():
            model = result["model"]
            path = os.path.join(directory, f"{name}.pkl")
            model.save(path)

        for name, result in self.mitigated_models.items():
            model = result["model"]
            path = os.path.join(directory, f"{name}_mitigated.pkl")
            model.save(path)

        logger.info(f"All models saved to {directory}")

    def load_model(self, path: str):
        """Load a model from disk and register it"""
        model = ModelWrapper.load(path)
        self.registry.register(model.name, model.model, model.preprocessor)
        logger.info(f"Loaded model {model.name} from {path}")
        return model
