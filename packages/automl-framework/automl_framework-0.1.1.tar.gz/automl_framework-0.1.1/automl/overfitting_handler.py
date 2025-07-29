"""
Overfitting handler module for AutoML framework.
Provides methods for detecting, preventing, and mitigating overfitting.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
from sklearn.base import BaseEstimator, clone
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
import logging

logger = logging.getLogger("AutoML")


class OverfittingHandler:
    """Handler for detecting and mitigating overfitting in models"""

    def __init__(self, problem_type: str = "classification"):
        """
        Initialize the overfitting handler

        Args:
            problem_type: 'classification' or 'regression'
        """
        self.problem_type = problem_type

    def detect_overfitting(
        self,
        train_metrics: Dict[str, float],
        test_metrics: Dict[str, float],
        model_name: str,
    ) -> Dict[str, Any]:
        """
        Detect if a model is overfitting based on train and test metrics

        Args:
            train_metrics: Dictionary of training metrics
            test_metrics: Dictionary of test metrics
            model_name: Name of the model

        Returns:
            Dictionary with overfitting assessment
        """
        result = {
            "is_overfitting": False,
            "overfitting_score": 0.0,
            "severity": "None",
            "details": {},
        }

        if self.problem_type == "classification":
            train_acc = train_metrics.get("accuracy", 0)
            test_acc = test_metrics.get("accuracy", 0)
            acc_gap = train_acc - test_acc

            train_prec = train_metrics.get("precision", 0)
            test_prec = test_metrics.get("precision", 0)
            prec_gap = train_prec - test_prec

            train_recall = train_metrics.get("recall", 0)
            test_recall = test_metrics.get("recall", 0)
            recall_gap = train_recall - test_recall

            train_f1 = train_metrics.get("f1", 0)
            test_f1 = test_metrics.get("f1", 0)
            f1_gap = train_f1 - test_f1

            overfitting_score = (
                0.4 * acc_gap + 0.2 * prec_gap + 0.2 * recall_gap + 0.2 * f1_gap
            )

            if overfitting_score > 0.6:
                severity = "Severe"
            elif overfitting_score > 0.3:
                severity = "Moderate"
            elif overfitting_score > 0.1:
                severity = "Slight"
            else:
                severity = "None"

            result["is_overfitting"] = overfitting_score > 0.1
            result["overfitting_score"] = overfitting_score
            result["severity"] = severity
            result["details"] = {
                "accuracy_gap": acc_gap,
                "precision_gap": prec_gap,
                "recall_gap": recall_gap,
                "f1_gap": f1_gap,
            }

        else:
            train_r2 = train_metrics.get("r2", 0)
            test_r2 = test_metrics.get("r2", 0)
            r2_gap = train_r2 - test_r2

            train_mse = train_metrics.get("mse", 1e-10)
            test_mse = test_metrics.get("mse", 0)
            mse_ratio = test_mse / train_mse if train_mse > 0 else float("inf")

            r2_overfitting = min(r2_gap / 0.3, 1.0)
            mse_overfitting = min(max(0, np.log10(mse_ratio)) / 2, 1.0)

            overfitting_score = 0.6 * r2_overfitting + 0.4 * mse_overfitting

            if overfitting_score > 0.6:
                severity = "Severe"
            elif overfitting_score > 0.3:
                severity = "Moderate"
            elif overfitting_score > 0.1:
                severity = "Slight"
            else:
                severity = "None"

            result["is_overfitting"] = overfitting_score > 0.1
            result["overfitting_score"] = overfitting_score
            result["severity"] = severity
            result["details"] = {"r2_gap": r2_gap, "mse_ratio": mse_ratio}

        result["model_specific"] = self._check_model_specific_risks(model_name)

        return result

    def _check_model_specific_risks(self, model_name: str) -> Dict[str, bool]:
        """Check for model-specific overfitting risks"""
        risks = {}

        risks["high_variance_model"] = any(
            name in model_name.lower() for name in ["tree", "forest", "boost", "xgb"]
        )

        risks["complex_model"] = any(
            name in model_name.lower() for name in ["neural", "mlp", "network", "deep"]
        )

        risks["flexible_model"] = any(
            name in model_name.lower() for name in ["svm", "svc", "svr", "poly", "rbf"]
        )

        return risks

    def get_prevention_params(self, model_name: str) -> Dict[str, Any]:
        """
        Get regularization parameters to prevent overfitting for a given model

        Args:
            model_name: Name of the model

        Returns:
            Dictionary of parameter settings to try
        """
        model_type = model_name.lower()

        if "tree" in model_type and not any(
            x in model_type for x in ["forest", "extra", "boost"]
        ):
            return {
                "max_depth": [3, 5, 7, 10, None],
                "min_samples_split": [2, 5, 10, 20],
                "min_samples_leaf": [1, 2, 4, 8],
                "max_features": ["sqrt", "log2", None],
            }

        elif any(x in model_type for x in ["randomforest", "random_forest"]):
            return {
                "max_depth": [5, 10, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None],
                "bootstrap": [True],
                "oob_score": [True],
            }

        elif any(x in model_type for x in ["boost", "xgb", "ada"]):
            return {
                "learning_rate": [0.01, 0.05, 0.1, 0.2],
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 5, 7, 10],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "subsample": [0.8, 0.9, 1.0] if "subsample" in model_type else [],
            }

        elif any(
            x in model_type
            for x in ["linear", "logistic", "regression", "ridge", "lasso"]
        ):
            if "logistic" in model_type or "classification" in model_type:
                return {
                    "C": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                    "penalty": (
                        ["l1", "l2", "elasticnet"]
                        if "elasticnet" in model_type
                        else ["l1", "l2"]
                    ),
                }
            else:
                return {
                    "alpha": [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                    "fit_intercept": [True, False],
                }

        elif any(x in model_type for x in ["svm", "svc", "svr"]):
            return {
                "C": [0.1, 1.0, 10.0, 100.0],
                "kernel": ["linear", "rbf", "poly"],
                "gamma": ["scale", "auto", 0.1, 0.01, 0.001],
            }

        elif any(x in model_type for x in ["mlp", "neural", "network"]):
            return {
                "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50)],
                "alpha": [0.0001, 0.001, 0.01, 0.1],
                "learning_rate": ["constant", "adaptive"],
                "early_stopping": [True],
            }

        elif any(x in model_type for x in ["knn", "neighbor"]):
            return {
                "n_neighbors": [3, 5, 7, 9, 11],
                "weights": ["uniform", "distance"],
                "p": [1, 2],
            }

        else:
            return {}

    def tune_model(
        self,
        model: BaseEstimator,
        X_train,
        y_train,
        X_val=None,
        y_val=None,
        cv=5,
        n_iter=10,
    ) -> Tuple[BaseEstimator, Dict[str, Any]]:
        """
        Tune a model to prevent overfitting

        Args:
            model: Base model to tune
            X_train, y_train: Training data
            X_val, y_val: Optional validation data (if None, CV is used)
            cv: Number of cross-validation folds
            n_iter: Number of parameter settings to try

        Returns:
            Tuple of (tuned_model, results)
        """
        model_type = type(model).__name__

        param_grid = self.get_prevention_params(model_type)

        if not param_grid:
            logger.warning(f"No prevention parameters available for {model_type}")
            return model, {"message": "No tuning performed"}

        base_model = clone(model)

        scoring = (
            "f1_weighted"
            if self.problem_type == "classification"
            else "neg_mean_squared_error"
        )

        logger.info(f"Tuning {model_type} to prevent overfitting")

        try:
            search = RandomizedSearchCV(
                base_model,
                param_distributions=param_grid,
                n_iter=n_iter,
                scoring=scoring,
                cv=cv,
                n_jobs=-1,
                random_state=42,
                return_train_score=True,
            )

            search.fit(X_train, y_train)

            results = {
                "best_params": search.best_params_,
                "best_score": search.best_score_,
                "train_score": search.cv_results_["mean_train_score"][
                    search.best_index_
                ],
                "test_score": search.best_score_,
                "train_test_diff": search.cv_results_["mean_train_score"][
                    search.best_index_
                ]
                - search.best_score_,
            }

            logger.info(f"Tuning complete. Best parameters: {results['best_params']}")

            return search.best_estimator_, results

        except Exception as e:
            logger.error(f"Error during model tuning: {str(e)}")
            return model, {"error": str(e)}

    def get_mitigation_strategies(
        self, model_name: str, overfitting_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get a list of strategies to mitigate overfitting

        Args:
            model_name: Name of the model
            overfitting_data: Data from detect_overfitting method

        Returns:
            List of strategies, each with a name, description, and implementation details
        """
        strategies = []

        if not overfitting_data.get("is_overfitting", False):
            return [
                {
                    "name": "No mitigation needed",
                    "description": "Model is not overfitting",
                }
            ]

        severity = overfitting_data.get("severity", "None")
        model_specific_risks = overfitting_data.get("model_specific", {})

        if (
            "high_variance_model" in model_specific_risks
            and model_specific_risks["high_variance_model"]
        ):
            strategies.append(
                {
                    "name": "Regularization",
                    "description": "Apply regularization to reduce model complexity",
                    "params": self._get_regularization_params(model_name, severity),
                    "priority": 1,
                }
            )

        if (
            "complex_model" in model_specific_risks
            and model_specific_risks["complex_model"]
        ):
            strategies.append(
                {
                    "name": "Early Stopping",
                    "description": "Stop training before overfitting occurs",
                    "params": {"early_stopping": True, "validation_fraction": 0.2},
                    "priority": 2,
                }
            )

        strategies.append(
            {
                "name": "Feature Selection",
                "description": "Select only the most important features",
                "method": "feature_importance",
                "priority": 3,
            }
        )

        strategies.append(
            {
                "name": "Ensemble Methods",
                "description": "Use bagging or boosting to reduce overfitting",
                "method": "ensemble",
                "priority": 4,
            }
        )

        strategies.append(
            {
                "name": "Cross-Validation",
                "description": "Use cross-validation for parameter selection",
                "method": "cv",
                "params": {"cv": 5},
                "priority": 5,
            }
        )

        return sorted(strategies, key=lambda x: x.get("priority", 10))

    def _get_regularization_params(
        self, model_name: str, severity: str
    ) -> Dict[str, Any]:
        """Get regularization parameters based on model type and overfitting severity"""
        model_type = model_name.lower()

        if severity == "Severe":
            strength = "high"
        elif severity == "Moderate":
            strength = "medium"
        else:
            strength = "low"

        if "tree" in model_type and not any(
            x in model_type for x in ["forest", "extra", "boost"]
        ):
            if strength == "high":
                return {"max_depth": 3, "min_samples_split": 10, "min_samples_leaf": 5}
            elif strength == "medium":
                return {"max_depth": 5, "min_samples_split": 5, "min_samples_leaf": 2}
            else:
                return {"max_depth": 10, "min_samples_split": 2, "min_samples_leaf": 1}

        elif any(x in model_type for x in ["randomforest", "random_forest"]):
            if strength == "high":
                return {
                    "max_depth": 5,
                    "min_samples_split": 10,
                    "min_samples_leaf": 5,
                    "max_features": "sqrt",
                }
            elif strength == "medium":
                return {
                    "max_depth": 10,
                    "min_samples_split": 5,
                    "min_samples_leaf": 2,
                    "max_features": "sqrt",
                }
            else:
                return {
                    "max_depth": 15,
                    "min_samples_split": 2,
                    "min_samples_leaf": 1,
                    "max_features": "sqrt",
                }

        elif any(x in model_type for x in ["boost", "xgb", "ada"]):
            if strength == "high":
                return {
                    "learning_rate": 0.01,
                    "max_depth": 3,
                    "subsample": 0.8,
                    "n_estimators": 100,
                }
            elif strength == "medium":
                return {
                    "learning_rate": 0.05,
                    "max_depth": 5,
                    "subsample": 0.9,
                    "n_estimators": 100,
                }
            else:
                return {
                    "learning_rate": 0.1,
                    "max_depth": 7,
                    "subsample": 1.0,
                    "n_estimators": 100,
                }

        elif any(
            x in model_type
            for x in ["logistic", "linear", "ridge", "lasso", "elasticnet"]
        ):
            if "logistic" in model_type:
                if strength == "high":
                    return {"C": 0.01, "penalty": "l2"}
                elif strength == "medium":
                    return {"C": 0.1, "penalty": "l2"}
                else:
                    return {"C": 1.0, "penalty": "l2"}
            else:
                if strength == "high":
                    return {"alpha": 10.0}
                elif strength == "medium":
                    return {"alpha": 1.0}
                else:
                    return {"alpha": 0.1}

        elif any(x in model_type for x in ["svm", "svc", "svr"]):
            if strength == "high":
                return {"C": 0.1, "kernel": "linear"}
            elif strength == "medium":
                return {"C": 1.0, "kernel": "linear"}
            else:
                return {"C": 10.0, "kernel": "rbf", "gamma": "scale"}

        elif any(x in model_type for x in ["mlp", "neural", "network"]):
            if strength == "high":
                return {
                    "alpha": 0.1,
                    "hidden_layer_sizes": (50,),
                    "early_stopping": True,
                }
            elif strength == "medium":
                return {
                    "alpha": 0.01,
                    "hidden_layer_sizes": (100,),
                    "early_stopping": True,
                }
            else:
                return {
                    "alpha": 0.001,
                    "hidden_layer_sizes": (100, 50),
                    "early_stopping": True,
                }

        else:
            return {}

    def apply_mitigation(
        self, model: BaseEstimator, strategy: Dict[str, Any], X_train, y_train
    ) -> Tuple[BaseEstimator, Dict[str, Any]]:
        """
        Apply a mitigation strategy to a model

        Args:
            model: Model to modify
            strategy: Strategy dictionary from get_mitigation_strategies
            X_train, y_train: Training data

        Returns:
            Tuple of (mitigated_model, results)
        """
        strategy_name = strategy.get("name", "")

        logger.info(f"Applying {strategy_name} strategy to mitigate overfitting")

        try:
            if strategy_name == "Regularization":
                params = strategy.get("params", {})

                new_model = clone(model)

                for param, value in params.items():
                    if hasattr(new_model, param):
                        setattr(new_model, param, value)

                new_model.fit(X_train, y_train)

                return new_model, {
                    "strategy": strategy_name,
                    "params_applied": params,
                    "success": True,
                }

            elif strategy_name == "Feature Selection":
                from sklearn.feature_selection import SelectFromModel

                selector = SelectFromModel(model, threshold="median")

                selector.fit(X_train, y_train)

                new_model = clone(model)

                X_train_selected = selector.transform(X_train)
                new_model.fit(X_train_selected, y_train)

                return new_model, {
                    "strategy": strategy_name,
                    "selector": selector,
                    "n_features_selected": X_train_selected.shape[1],
                    "success": True,
                }

            elif strategy_name == "Ensemble Methods":
                from sklearn.ensemble import BaggingClassifier, BaggingRegressor

                if self.problem_type == "classification":
                    ensemble = BaggingClassifier(
                        base_estimator=model, n_estimators=10, random_state=42
                    )
                else:
                    ensemble = BaggingRegressor(
                        base_estimator=model, n_estimators=10, random_state=42
                    )

                ensemble.fit(X_train, y_train)

                return ensemble, {
                    "strategy": strategy_name,
                    "ensemble_type": type(ensemble).__name__,
                    "success": True,
                }

            elif strategy_name == "Early Stopping":
                if hasattr(model, "early_stopping") or hasattr(
                    model, "n_iter_no_change"
                ):
                    new_model = clone(model)

                    if hasattr(new_model, "early_stopping"):
                        setattr(new_model, "early_stopping", True)

                    if hasattr(new_model, "n_iter_no_change"):
                        setattr(new_model, "n_iter_no_change", 5)

                    if hasattr(new_model, "validation_fraction"):
                        setattr(new_model, "validation_fraction", 0.2)

                    new_model.fit(X_train, y_train)

                    return new_model, {"strategy": strategy_name, "success": True}
                else:
                    return model, {
                        "strategy": strategy_name,
                        "success": False,
                        "message": "Model does not support early stopping",
                    }

            elif strategy_name == "Cross-Validation":
                tuned_model, results = self.tune_model(
                    model,
                    X_train,
                    y_train,
                    cv=strategy.get("params", {}).get("cv", 5),
                    n_iter=10,
                )

                results["strategy"] = strategy_name
                results["success"] = True

                return tuned_model, results

            else:
                return model, {
                    "strategy": strategy_name,
                    "success": False,
                    "message": "Unknown strategy or no mitigation needed",
                }

        except Exception as e:
            logger.error(f"Error applying {strategy_name} strategy: {str(e)}")
            return model, {"strategy": strategy_name, "success": False, "error": str(e)}
