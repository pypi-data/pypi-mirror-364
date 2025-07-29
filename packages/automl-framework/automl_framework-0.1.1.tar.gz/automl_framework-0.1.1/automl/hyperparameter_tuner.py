"""
Comprehensive hyperparameter tuning module for the AutoML framework.
Provides advanced hyperparameter optimization capabilities using various search strategies.
"""

import numpy as np
import pandas as pd
import time
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    KFold,
    StratifiedKFold,
)
from sklearn.base import BaseEstimator, clone
import matplotlib.pyplot as plt
import seaborn as sns
from functools import partial
import joblib
import os

logger = logging.getLogger("AutoML")

try:
    from sklearn.experimental import enable_halving_search_cv
    from sklearn.model_selection import HalvingGridSearchCV, HalvingRandomSearchCV

    HALVING_SEARCH_AVAILABLE = True
except ImportError:
    HALVING_SEARCH_AVAILABLE = False
    logger.warning("HalvingGridSearchCV not available. Using regular grid search.")

try:
    from skopt import BayesSearchCV
    from skopt.space import Real, Integer, Categorical

    BAYESIAN_SEARCH_AVAILABLE = True
except ImportError:
    BAYESIAN_SEARCH_AVAILABLE = False
    logger.warning(
        "BayesSearchCV not available. Install scikit-optimize for Bayesian optimization."
    )

try:
    from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
    from hyperopt.pyll import scope

    HYPEROPT_AVAILABLE = True
except ImportError:
    HYPEROPT_AVAILABLE = False
    logger.warning("Hyperopt not available. Install hyperopt for more advanced tuning.")


class HyperparameterTuner:
    """
    Advanced hyperparameter tuning class with multiple search strategies
    """

    def __init__(
        self,
        problem_type: str = "classification",
        cv: int = 5,
        random_state: int = 42,
        n_jobs: int = -1,
        verbose: int = 1,
    ):
        """
        Initialize the hyperparameter tuner

        Args:
            problem_type: 'classification' or 'regression'
            cv: Number of cross-validation folds
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 for all CPUs)
            verbose: Verbosity level
        """
        self.problem_type = problem_type
        self.cv = cv
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.verbose = verbose

        if problem_type == "classification":
            self.scoring = "f1_weighted"
        else:
            self.scoring = "neg_mean_squared_error"

        self.results = {}
        self.best_params = {}
        self.best_estimators = {}
        self.tuning_history = {}

    def set_scoring(self, scoring: str):
        """
        Set the scoring metric

        Args:
            scoring: Scoring metric name compatible with sklearn
        """
        self.scoring = scoring
        logger.info(f"Scoring metric set to: {scoring}")

    def get_param_grid(self, model_name: str, search_type: str = "grid") -> Dict:
        """
        Get parameter grid for hyperparameter tuning based on model type

        Args:
            model_name: Name or type of the model
            search_type: 'grid', 'random', 'bayesian', or 'hyperopt'

        Returns:
            Dictionary with parameter grid
        """
        model_type = model_name.lower()

        if search_type in ["grid", "random", "halving"]:
            if "tree" in model_type and not any(
                x in model_type for x in ["forest", "extra", "boost"]
            ):
                return {
                    "max_depth": [3, 5, 7, 10, 15, 20, None],
                    "min_samples_split": [2, 5, 10, 15, 20],
                    "min_samples_leaf": [1, 2, 4, 8],
                    "max_features": ["sqrt", "log2", None],
                    "criterion": (
                        ["gini", "entropy"]
                        if self.problem_type == "classification"
                        else ["squared_error", "friedman_mse", "absolute_error"]
                    ),
                }

            elif any(x in model_type for x in ["randomforest", "random_forest"]):
                return {
                    "n_estimators": [50, 100, 200, 300],
                    "max_depth": [5, 10, 20, 30, None],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "max_features": ["sqrt", "log2", None],
                    "bootstrap": [True, False],
                    "criterion": (
                        ["gini", "entropy"]
                        if self.problem_type == "classification"
                        else ["squared_error", "friedman_mse", "absolute_error"]
                    ),
                }

            elif "gradientboosting" in model_type or "gradient_boosting" in model_type:
                return {
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [50, 100, 200, 300],
                    "max_depth": [3, 5, 7, 9],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "subsample": [0.8, 0.9, 1.0],
                    "max_features": ["sqrt", "log2", None],
                }

            elif "adaboost" in model_type or "ada_boost" in model_type:
                return {
                    "n_estimators": [50, 100, 200],
                    "learning_rate": [0.01, 0.1, 0.5, 1.0],
                    "algorithm": (
                        ["SAMME", "SAMME.R"]
                        if self.problem_type == "classification"
                        else ["SAMME"]
                    ),
                }

            elif "xgboost" in model_type or "xgb" in model_type:
                return {
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [50, 100, 200, 300],
                    "max_depth": [3, 5, 7, 9],
                    "min_child_weight": [1, 3, 5, 7],
                    "gamma": [0, 0.1, 0.2, 0.3],
                    "subsample": [0.6, 0.8, 1.0],
                    "colsample_bytree": [0.6, 0.8, 1.0],
                    "reg_alpha": [0, 0.1, 1.0],
                    "reg_lambda": [0, 0.1, 1.0],
                }

            elif "lightgbm" in model_type or "lgbm" in model_type:
                return {
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [50, 100, 200, 300],
                    "max_depth": [3, 5, 7, 9, -1],
                    "num_leaves": [31, 50, 70, 90],
                    "min_child_samples": [10, 20, 30],
                    "subsample": [0.6, 0.8, 1.0],
                    "colsample_bytree": [0.6, 0.8, 1.0],
                    "reg_alpha": [0, 0.1, 1.0],
                    "reg_lambda": [0, 0.1, 1.0],
                }

            elif "catboost" in model_type:
                return {
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "iterations": [50, 100, 200, 300],
                    "depth": [4, 6, 8, 10],
                    "l2_leaf_reg": [1, 3, 5, 7],
                    "bagging_temperature": [0, 1, 10],
                    "random_strength": [0.1, 1, 10],
                    "border_count": [32, 64, 128],
                }

            elif any(
                x in model_type
                for x in ["linear", "logistic", "regression", "ridge", "lasso"]
            ):
                if "logistic" in model_type or (
                    self.problem_type == "classification" and "regression" in model_type
                ):
                    return {
                        "C": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                        "penalty": ["l1", "l2", "elasticnet", "none"],
                        "solver": ["lbfgs", "liblinear", "newton-cg", "sag", "saga"],
                        "max_iter": [100, 500, 1000, 2000],
                    }
                elif "ridge" in model_type:
                    return {
                        "alpha": [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                        "fit_intercept": [True, False],
                        "solver": [
                            "auto",
                            "svd",
                            "cholesky",
                            "lsqr",
                            "sparse_cg",
                            "sag",
                            "saga",
                        ],
                    }
                elif "lasso" in model_type:
                    return {
                        "alpha": [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                        "fit_intercept": [True, False],
                        "max_iter": [100, 500, 1000, 2000],
                    }
                else:
                    return {"fit_intercept": [True, False], "n_jobs": [None, 1, -1]}

            elif any(x in model_type for x in ["svm", "svc", "svr"]):
                return {
                    "C": [0.1, 1.0, 10.0, 100.0],
                    "kernel": ["linear", "rbf", "poly", "sigmoid"],
                    "gamma": ["scale", "auto", 0.1, 0.01, 0.001],
                    "degree": [2, 3, 4] if "poly" in model_type else [3],
                    "shrinking": [True, False],
                }

            elif any(x in model_type for x in ["mlp", "neural", "network"]):
                return {
                    "hidden_layer_sizes": [
                        (50,),
                        (100,),
                        (50, 50),
                        (100, 50),
                        (100, 100),
                    ],
                    "activation": ["relu", "tanh", "logistic"],
                    "solver": ["adam", "sgd", "lbfgs"],
                    "alpha": [0.0001, 0.001, 0.01, 0.1],
                    "learning_rate": ["constant", "adaptive", "invscaling"],
                    "max_iter": [200, 500, 1000],
                    "early_stopping": [True, False],
                }

            elif any(x in model_type for x in ["knn", "neighbor"]):
                return {
                    "n_neighbors": [3, 5, 7, 9, 11, 15],
                    "weights": ["uniform", "distance"],
                    "algorithm": ["auto", "ball_tree", "kd_tree", "brute"],
                    "leaf_size": [10, 20, 30, 40, 50],
                    "p": [1, 2],
                }

            else:
                logger.warning(
                    f"No specific parameter grid available for {model_name}. Using minimal default grid."
                )
                return {"random_state": [self.random_state, None]}

        elif search_type == "bayesian" and BAYESIAN_SEARCH_AVAILABLE:
            if "tree" in model_type and not any(
                x in model_type for x in ["forest", "extra", "boost"]
            ):
                return {
                    "max_depth": Integer(3, 30),
                    "min_samples_split": Integer(2, 30),
                    "min_samples_leaf": Integer(1, 15),
                    "max_features": Categorical(["sqrt", "log2", None]),
                    "criterion": (
                        Categorical(["gini", "entropy"])
                        if self.problem_type == "classification"
                        else Categorical(
                            ["squared_error", "friedman_mse", "absolute_error"]
                        )
                    ),
                }

            elif any(x in model_type for x in ["randomforest", "random_forest"]):
                return {
                    "n_estimators": Integer(50, 500),
                    "max_depth": Integer(5, 30),
                    "min_samples_split": Integer(2, 20),
                    "min_samples_leaf": Integer(1, 10),
                    "max_features": Categorical(["sqrt", "log2", None]),
                    "bootstrap": Categorical([True, False]),
                    "criterion": (
                        Categorical(["gini", "entropy"])
                        if self.problem_type == "classification"
                        else Categorical(
                            ["squared_error", "friedman_mse", "absolute_error"]
                        )
                    ),
                }

            elif "gradientboosting" in model_type or "gradient_boosting" in model_type:
                return {
                    "learning_rate": Real(0.01, 0.3, prior="log-uniform"),
                    "n_estimators": Integer(50, 500),
                    "max_depth": Integer(3, 10),
                    "min_samples_split": Integer(2, 20),
                    "min_samples_leaf": Integer(1, 10),
                    "subsample": Real(0.6, 1.0, prior="uniform"),
                    "max_features": Categorical(["sqrt", "log2", None]),
                }

            elif "adaboost" in model_type or "ada_boost" in model_type:
                return {
                    "n_estimators": Integer(50, 300),
                    "learning_rate": Real(0.01, 1.0, prior="log-uniform"),
                    "algorithm": (
                        Categorical(["SAMME", "SAMME.R"])
                        if self.problem_type == "classification"
                        else Categorical(["SAMME"])
                    ),
                }

            else:
                logger.warning(
                    f"No specific Bayesian parameter space for {model_name}. Using defaults."
                )
                return None

        elif search_type == "hyperopt" and HYPEROPT_AVAILABLE:
            if "tree" in model_type and not any(
                x in model_type for x in ["forest", "extra", "boost"]
            ):
                return {
                    "max_depth": scope.int(hp.quniform("max_depth", 3, 30, 1)),
                    "min_samples_split": scope.int(
                        hp.quniform("min_samples_split", 2, 30, 1)
                    ),
                    "min_samples_leaf": scope.int(
                        hp.quniform("min_samples_leaf", 1, 15, 1)
                    ),
                    "max_features": hp.choice("max_features", ["sqrt", "log2", None]),
                    "criterion": hp.choice(
                        "criterion",
                        (
                            ["gini", "entropy"]
                            if self.problem_type == "classification"
                            else ["squared_error", "friedman_mse", "absolute_error"]
                        ),
                    ),
                }

            elif any(x in model_type for x in ["randomforest", "random_forest"]):
                return {
                    "n_estimators": scope.int(hp.quniform("n_estimators", 50, 500, 10)),
                    "max_depth": scope.int(hp.quniform("max_depth", 5, 30, 1)),
                    "min_samples_split": scope.int(
                        hp.quniform("min_samples_split", 2, 20, 1)
                    ),
                    "min_samples_leaf": scope.int(
                        hp.quniform("min_samples_leaf", 1, 10, 1)
                    ),
                    "max_features": hp.choice("max_features", ["sqrt", "log2", None]),
                    "bootstrap": hp.choice("bootstrap", [True, False]),
                    "criterion": hp.choice(
                        "criterion",
                        (
                            ["gini", "entropy"]
                            if self.problem_type == "classification"
                            else ["squared_error", "friedman_mse", "absolute_error"]
                        ),
                    ),
                }

            else:
                logger.warning(
                    f"No specific Hyperopt space for {model_name}. Using minimal defaults."
                )
                return {}

        else:
            logger.warning(
                f"Unsupported search type: {search_type}. Using grid search parameters."
            )
            return self.get_param_grid(model_name, "grid")

    def tune_model(
        self,
        model_name: str,
        model_instance: BaseEstimator,
        X,
        y,
        param_grid: Optional[Dict] = None,
        search_type: str = "grid",
        n_iter: int = 20,
        n_splits: int = 5,
        refit: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning on a model

        Args:
            model_name: Name of the model
            model_instance: Model instance to tune
            X: Features
            y: Target
            param_grid: Parameter grid (if None, automatically generated)
            search_type: 'grid', 'random', 'halving', 'bayesian', or 'hyperopt'
            n_iter: Number of iterations for random search, bayesian opt, or hyperopt
            n_splits: Number of cross-validation splits
            refit: Whether to refit the model with best parameters

        Returns:
            Dictionary with tuning results
        """
        start_time = time.time()

        if param_grid is None:
            param_grid = self.get_param_grid(model_name, search_type)

        logger.info(f"Tuning {model_name} using {search_type} search...")

        if self.problem_type == "classification":
            cv = StratifiedKFold(
                n_splits=n_splits, shuffle=True, random_state=self.random_state
            )
        else:
            cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)

        best_estimator = None
        best_params = None
        best_score = None
        cv_results = None
        search_history = None

        try:
            if search_type == "grid":
                search = GridSearchCV(
                    estimator=model_instance,
                    param_grid=param_grid,
                    scoring=self.scoring,
                    cv=cv,
                    n_jobs=self.n_jobs,
                    verbose=self.verbose,
                    refit=refit,
                    return_train_score=True,
                )

                search.fit(X, y)
                best_estimator = search.best_estimator_
                best_params = search.best_params_
                best_score = search.best_score_
                cv_results = search.cv_results_

            elif search_type == "random":
                search = RandomizedSearchCV(
                    estimator=model_instance,
                    param_distributions=param_grid,
                    n_iter=n_iter,
                    scoring=self.scoring,
                    cv=cv,
                    n_jobs=self.n_jobs,
                    verbose=self.verbose,
                    refit=refit,
                    random_state=self.random_state,
                    return_train_score=True,
                )

                search.fit(X, y)
                best_estimator = search.best_estimator_
                best_params = search.best_params_
                best_score = search.best_score_
                cv_results = search.cv_results_

            elif search_type == "halving" and HALVING_SEARCH_AVAILABLE:
                if "random" in model_name.lower():
                    search = HalvingRandomSearchCV(
                        estimator=model_instance,
                        param_distributions=param_grid,
                        scoring=self.scoring,
                        cv=cv,
                        n_jobs=self.n_jobs,
                        verbose=self.verbose,
                        refit=refit,
                        random_state=self.random_state,
                        return_train_score=True,
                    )
                else:
                    search = HalvingGridSearchCV(
                        estimator=model_instance,
                        param_grid=param_grid,
                        scoring=self.scoring,
                        cv=cv,
                        n_jobs=self.n_jobs,
                        verbose=self.verbose,
                        refit=refit,
                        random_state=self.random_state,
                        return_train_score=True,
                    )

                search.fit(X, y)
                best_estimator = search.best_estimator_
                best_params = search.best_params_
                best_score = search.best_score_
                cv_results = search.cv_results_

            elif search_type == "bayesian" and BAYESIAN_SEARCH_AVAILABLE:
                search = BayesSearchCV(
                    estimator=model_instance,
                    search_spaces=param_grid,
                    n_iter=n_iter,
                    scoring=self.scoring,
                    cv=cv,
                    n_jobs=self.n_jobs,
                    verbose=self.verbose,
                    refit=refit,
                    random_state=self.random_state,
                    return_train_score=True,
                )

                search.fit(X, y)
                best_estimator = search.best_estimator_
                best_params = search.best_params_
                best_score = search.best_score_
                cv_results = search.cv_results_
                search_history = search.optimizer_results_

            elif search_type == "hyperopt" and HYPEROPT_AVAILABLE:

                def objective(
                    params, model=None, X=None, y=None, cv=None, scoring=None
                ):
                    model_copy = clone(model)
                    try:
                        model_copy.set_params(**params)
                    except Exception as e:
                        logger.warning(f"Error setting params {params}: {str(e)}")
                        return {"loss": float("inf"), "status": STATUS_OK}

                    try:
                        scores = cross_val_score(
                            model_copy, X, y, cv=cv, scoring=scoring, n_jobs=self.n_jobs
                        )
                        avg_score = np.mean(scores)

                        if "neg_" in scoring:
                            loss = -avg_score
                        else:
                            loss = -avg_score

                        return {
                            "loss": loss,
                            "status": STATUS_OK,
                            "model_params": params,
                            "score": avg_score,
                            "cv_scores": scores.tolist(),
                        }
                    except Exception as e:
                        logger.warning(f"Error in CV with params {params}: {str(e)}")
                        return {"loss": float("inf"), "status": STATUS_OK}

                trials = Trials()

                obj_func = partial(
                    objective,
                    model=model_instance,
                    X=X,
                    y=y,
                    cv=cv,
                    scoring=self.scoring,
                )

                result = fmin(
                    fn=obj_func,
                    space=param_grid,
                    algo=tpe.suggest,
                    max_evals=n_iter,
                    trials=trials,
                    rstate=np.random.RandomState(self.random_state),
                )

                trial_results = [
                    t["result"]
                    for t in trials.trials
                    if t["result"]["status"] == STATUS_OK
                ]
                if trial_results:
                    best_trial = min(trial_results, key=lambda x: x["loss"])
                    best_params = best_trial["model_params"]
                    best_score = best_trial["score"]
                    search_history = trials

                    if refit:
                        best_estimator = clone(model_instance)
                        best_estimator.set_params(**best_params)
                        best_estimator.fit(X, y)

                    cv_results = {
                        "params": [
                            t["result"]["model_params"]
                            for t in trials.trials
                            if "model_params" in t["result"]
                        ],
                        "mean_test_score": [
                            (
                                t["result"]["score"]
                                if "score" in t["result"]
                                else float("-inf")
                            )
                            for t in trials.trials
                        ],
                        "std_test_score": [
                            (
                                np.std(t["result"]["cv_scores"])
                                if "cv_scores" in t["result"]
                                else 0
                            )
                            for t in trials.trials
                        ],
                    }
                else:
                    logger.warning(
                        "No successful Hyperopt trials. Falling back to default model."
                    )
                    best_estimator = model_instance
                    best_params = {}
                    best_score = float("-inf")

            else:
                logger.warning(
                    f"Unsupported or unavailable search type: {search_type}. Falling back to grid search."
                )
                return self.tune_model(
                    model_name,
                    model_instance,
                    X,
                    y,
                    param_grid,
                    "grid",
                    n_iter,
                    n_splits,
                    refit,
                )

            tuning_time = time.time() - start_time

            result = {
                "model_name": model_name,
                "best_params": best_params,
                "best_score": best_score,
                "best_estimator": best_estimator,
                "cv_results": cv_results,
                "search_type": search_type,
                "tuning_time": tuning_time,
                "search_history": search_history,
            }

            self.results[model_name] = result
            self.best_params[model_name] = best_params
            self.best_estimators[model_name] = best_estimator

            logger.info(
                f"Tuning completed for {model_name} in {tuning_time:.2f} seconds."
            )
            logger.info(f"Best parameters: {best_params}")
            logger.info(f"Best score: {best_score:.4f}")

            return result

        except Exception as e:
            logger.error(f"Error tuning {model_name}: {str(e)}")
            logger.error(traceback.format_exc())

            return {
                "model_name": model_name,
                "error": str(e),
                "status": "failed",
                "tuning_time": time.time() - start_time,
            }

    def tune_multiple_models(
        self,
        models_dict: Dict[str, BaseEstimator],
        X,
        y,
        search_type: str = "random",
        n_iter: int = 20,
    ) -> Dict[str, Dict]:
        """
        Tune multiple models at once

        Args:
            models_dict: Dictionary mapping model names to model instances
            X: Features
            y: Target
            search_type: Search type to use
            n_iter: Number of iterations for random, bayesian or hyperopt search

        Returns:
            Dictionary with tuning results for each model
        """
        results = {}

        for name, model in models_dict.items():
            logger.info(f"Tuning model {name}...")
            result = self.tune_model(
                name, model, X, y, search_type=search_type, n_iter=n_iter
            )
            results[name] = result

        return results

    def get_best_model(self) -> Tuple[str, BaseEstimator, float]:
        """
        Get the best model from all tuned models

        Returns:
            Tuple of (model_name, best_estimator, best_score)
        """
        if not self.results:
            raise ValueError("No models have been tuned yet")

        best_model_name = max(
            self.results,
            key=lambda name: self.results[name].get("best_score", float("-inf")),
        )
        best_estimator = self.best_estimators.get(best_model_name)
        best_score = self.results[best_model_name].get("best_score", float("-inf"))

        return best_model_name, best_estimator, best_score

    def get_tuning_summary(self) -> pd.DataFrame:
        """
        Get a summary DataFrame of all tuning results

        Returns:
            DataFrame with tuning results
        """
        if not self.results:
            raise ValueError("No models have been tuned yet")

        data = []

        for name, result in self.results.items():
            row = {
                "model": name,
                "best_score": result.get("best_score", float("-inf")),
                "tuning_time": result.get("tuning_time", None),
                "search_type": result.get("search_type", None),
                "status": "success" if "best_score" in result else "failed",
            }

            best_params = result.get("best_params", {})
            if best_params:
                for i, (param, value) in enumerate(best_params.items()):
                    if i >= 5:
                        break
                    row[f"param_{param}"] = value

            data.append(row)

        df = pd.DataFrame(data)

        if "best_score" in df.columns:
            df = df.sort_values("best_score", ascending=False)

        return df

    def plot_tuning_results(
        self,
        model_name: str,
        param1: str,
        param2: Optional[str] = None,
        output_file: Optional[str] = None,
    ):
        """
        Plot tuning results to visualize parameter importance

        Args:
            model_name: Name of the model to plot
            param1: First parameter to plot
            param2: Optional second parameter for heatmap
            output_file: Optional file path to save plot
        """
        if model_name not in self.results:
            raise ValueError(f"Model {model_name} has not been tuned yet")

        result = self.results[model_name]

        if "cv_results" not in result:
            raise ValueError(f"No CV results available for {model_name}")

        cv_results = result["cv_results"]

        try:
            params = pd.DataFrame(cv_results["params"])
            scores = cv_results["mean_test_score"]

            if param1 not in params.columns:
                raise ValueError(f"Parameter {param1} not found in tuning results")

            plt.figure(figsize=(10, 6))

            if param2 is not None:
                if param2 not in params.columns:
                    raise ValueError(f"Parameter {param2} not found in tuning results")

                param1_numeric = pd.api.types.is_numeric_dtype(params[param1])
                param2_numeric = pd.api.types.is_numeric_dtype(params[param2])

                if param1_numeric and param2_numeric:
                    pivot = pd.DataFrame(
                        {
                            param1: params[param1],
                            param2: params[param2],
                            "score": scores,
                        }
                    ).pivot_table(
                        index=param1, columns=param2, values="score", aggfunc="mean"
                    )

                    sns.heatmap(pivot, annot=True, fmt=".4f", cmap="viridis")
                    plt.title(f"Parameter Tuning Heatmap for {model_name}")

                else:
                    plt.scatter(
                        x=params[param1],
                        y=scores,
                        c=(
                            params[param2].astype("category").cat.codes
                            if not param2_numeric
                            else params[param2]
                        ),
                        cmap="viridis",
                        alpha=0.7,
                    )

                    if not param2_numeric:
                        categories = params[param2].unique()
                        handles = []
                        for i, cat in enumerate(categories):
                            handles.append(
                                plt.scatter([], [], c=[i], cmap="viridis", label=cat)
                            )
                        plt.legend(handles=handles, title=param2)
                    else:
                        plt.colorbar(label=param2)

                    plt.xlabel(param1)
                    plt.ylabel("Score")
                    plt.title(f"Parameter Tuning Results for {model_name}")

            else:
                param1_numeric = pd.api.types.is_numeric_dtype(params[param1])

                if param1_numeric:
                    plt.scatter(params[param1], scores, alpha=0.7)
                    plt.xlabel(param1)
                    plt.ylabel("Score")

                else:
                    data = pd.DataFrame({"param": params[param1], "score": scores})
                    sns.boxplot(x="param", y="score", data=data)
                    plt.xlabel(param1)
                    plt.ylabel("Score")

                plt.title(f"Parameter Tuning Results for {model_name}")

            plt.tight_layout()

            if output_file:
                plt.savefig(output_file)
                logger.info(f"Plot saved to {output_file}")

            plt.show()

        except Exception as e:
            logger.error(f"Error plotting tuning results: {str(e)}")
            logger.error(traceback.format_exc())

    def plot_parameter_importance(
        self, model_name: str, n_top_params: int = 10, output_file: Optional[str] = None
    ):
        """
        Plot parameter importance using correlation with scores

        Args:
            model_name: Name of the model
            n_top_params: Number of top parameters to show
            output_file: Optional file path to save plot
        """
        if model_name not in self.results:
            raise ValueError(f"Model {model_name} has not been tuned yet")

        result = self.results[model_name]

        if "cv_results" not in result:
            raise ValueError(f"No CV results available for {model_name}")

        try:
            cv_results = result["cv_results"]

            param_names = []
            for param_name in cv_results["params"][0].keys():
                param_names.append(param_name)

            importance = {}

            params_df = pd.DataFrame(cv_results["params"])
            scores = cv_results["mean_test_score"]

            for param in param_names:
                if not pd.api.types.is_numeric_dtype(params_df[param]):
                    try:
                        params_df[param] = pd.to_numeric(
                            params_df[param], errors="raise"
                        )
                    except Exception:
                        continue

                correlation = np.corrcoef(params_df[param], scores)[0, 1]

                importance[param] = abs(correlation)

            importance = {
                k: v
                for k, v in sorted(
                    importance.items(), key=lambda item: item[1], reverse=True
                )
            }

            top_params = list(importance.keys())[:n_top_params]
            top_importance = [importance[param] for param in top_params]

            plt.figure(figsize=(10, 6))
            plt.barh(top_params, top_importance, color="skyblue")
            plt.xlabel("Importance (|Correlation|)")
            plt.ylabel("Parameter")
            plt.title(f"Parameter Importance for {model_name}")
            plt.tight_layout()

            if output_file:
                plt.savefig(output_file)
                logger.info(f"Plot saved to {output_file}")

            plt.show()

        except Exception as e:
            logger.error(f"Error calculating parameter importance: {str(e)}")
            logger.error(traceback.format_exc())

    def save_tuning_results(self, directory: str, model_name: Optional[str] = None):
        """
        Save tuning results to disk

        Args:
            directory: Directory to save results
            model_name: Optional model name (if None, save all)
        """
        os.makedirs(directory, exist_ok=True)

        if model_name is not None:
            if model_name not in self.results:
                raise ValueError(f"Model {model_name} has not been tuned yet")

            result = self.results[model_name]

            if "best_estimator" in result and result["best_estimator"] is not None:
                estimator_path = os.path.join(
                    directory, f"{model_name}_best_estimator.pkl"
                )
                joblib.dump(result["best_estimator"], estimator_path)
                logger.info(
                    f"Best estimator for {model_name} saved to {estimator_path}"
                )

            result_copy = result.copy()
            result_copy.pop("best_estimator", None)

            results_path = os.path.join(directory, f"{model_name}_tuning_results.pkl")
            joblib.dump(result_copy, results_path)
            logger.info(f"Tuning results for {model_name} saved to {results_path}")

            try:
                importance_path = os.path.join(
                    directory, f"{model_name}_parameter_importance.png"
                )
                self.plot_parameter_importance(model_name, output_file=importance_path)

                cv_results = result.get("cv_results", {})
                if (
                    "params" in cv_results
                    and cv_results["params"]
                    and len(cv_results["params"][0]) >= 2
                ):
                    param_names = list(cv_results["params"][0].keys())
                    tuning_path = os.path.join(
                        directory, f"{model_name}_tuning_plot.png"
                    )
                    self.plot_tuning_results(
                        model_name, param_names[0], param_names[1], tuning_path
                    )
            except Exception as e:
                logger.warning(f"Error generating plots for {model_name}: {str(e)}")

        else:
            for name in self.results:
                try:
                    self.save_tuning_results(directory, name)
                except Exception as e:
                    logger.error(f"Error saving results for {name}: {str(e)}")

            summary_df = self.get_tuning_summary()
            summary_path = os.path.join(directory, "tuning_summary.csv")
            summary_df.to_csv(summary_path, index=False)
            logger.info(f"Tuning summary saved to {summary_path}")

    def load_tuning_results(self, directory: str, model_name: str):
        """
        Load tuning results from disk

        Args:
            directory: Directory with saved results
            model_name: Model name to load

        Returns:
            Loaded results dictionary
        """
        results_path = os.path.join(directory, f"{model_name}_tuning_results.pkl")
        estimator_path = os.path.join(directory, f"{model_name}_best_estimator.pkl")

        if not os.path.exists(results_path):
            raise ValueError(f"Tuning results file not found: {results_path}")

        results = joblib.load(results_path)

        if os.path.exists(estimator_path):
            estimator = joblib.load(estimator_path)
            results["best_estimator"] = estimator

        self.results[model_name] = results
        self.best_params[model_name] = results.get("best_params", {})

        if "best_estimator" in results:
            self.best_estimators[model_name] = results["best_estimator"]

        logger.info(f"Loaded tuning results for {model_name}")

        return results
