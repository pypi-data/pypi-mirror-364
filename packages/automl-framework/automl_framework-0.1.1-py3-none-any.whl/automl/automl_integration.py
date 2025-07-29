"""
Integration for the hyperparameter_tuner module with the main AutoML framework.
This file adds hyperparameter tuning capabilities to your existing AutoML system.
"""

import os
import logging
from typing import Dict, Any, Optional, Union, List
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator

from hyperparameter_tuner import HyperparameterTuner

logger = logging.getLogger("AutoML")


class TuningIntegrator:
    """
    Integrates hyperparameter tuning with the AutoML framework
    """

    def __init__(self, automl_instance, output_dir: str = "tuning_results"):
        """
        Initialize the tuning integrator

        Args:
            automl_instance: The AutoML instance to integrate with
            output_dir: Directory to save tuning results
        """
        self.automl = automl_instance
        self.problem_type = automl_instance.pipeline.problem_type
        self.output_dir = output_dir
        self.random_state = automl_instance.pipeline.random_state

        self.tuner = HyperparameterTuner(
            problem_type=self.problem_type, random_state=self.random_state
        )

        os.makedirs(output_dir, exist_ok=True)

    def tune_models(
        self,
        X,
        y,
        models_to_tune: Optional[List[str]] = None,
        search_type: str = "random",
        n_iter: int = 20,
        cv: int = 5,
        register_best: bool = True,
        save_results: bool = True,
    ) -> pd.DataFrame:
        """
        Tune selected models and optionally register the best versions

        Args:
            X: Features for tuning
            y: Target for tuning
            models_to_tune: List of model names to tune (None = all)
            search_type: 'grid', 'random', 'halving', 'bayesian', or 'hyperopt'
            n_iter: Number of iterations for random/bayesian/hyperopt search
            cv: Number of cross-validation folds
            register_best: Whether to register tuned models back to AutoML
            save_results: Whether to save tuning results to disk

        Returns:
            DataFrame with tuning summary
        """
        logger.info(f"Starting hyperparameter tuning with {search_type} search")

        all_models = self.automl.pipeline.registry.get_models()

        if models_to_tune is not None:
            models = {
                name: all_models[name] for name in models_to_tune if name in all_models
            }
            if not models:
                raise ValueError(
                    f"None of the specified models {models_to_tune} found in registry"
                )
        else:
            models = all_models

        logger.info(f"Tuning {len(models)} models: {', '.join(models.keys())}")

        sklearn_models = {}
        for name, model_wrapper in models.items():
            sklearn_models[name] = model_wrapper.model

        self.tuner.tune_multiple_models(
            sklearn_models, X, y, search_type=search_type, n_iter=n_iter
        )

        summary = self.tuner.get_tuning_summary()

        if register_best:
            for name, tuning_result in self.tuner.results.items():
                if (
                    "best_estimator" in tuning_result
                    and tuning_result["best_estimator"] is not None
                ):
                    preprocessor = models[name].preprocessor

                    best_params = tuning_result["best_params"]
                    best_score = tuning_result["best_score"]

                    logger.info(
                        f"Registering tuned model {name} with score {best_score:.4f}"
                    )

                    tuned_model_name = f"{name}_tuned"
                    self.automl.register_model(
                        tuned_model_name, tuning_result["best_estimator"], preprocessor
                    )

                    logger.info(f"Tuned parameters for {name}: {best_params}")

        if save_results:
            self.tuner.save_tuning_results(self.output_dir)

            summary_path = os.path.join(self.output_dir, "tuning_summary.csv")
            summary.to_csv(summary_path, index=False)
            logger.info(f"Tuning summary saved to {summary_path}")

        return summary

    def get_best_models(self, top_n: int = 1) -> List[Dict[str, Any]]:
        """
        Get the top N best models from tuning

        Args:
            top_n: Number of top models to return

        Returns:
            List of dictionaries with model info
        """
        if not self.tuner.results:
            raise ValueError("No tuning results available. Run tune_models first.")

        all_results = []
        for name, result in self.tuner.results.items():
            if "best_score" in result and result["best_score"] is not None:
                all_results.append(
                    {
                        "model_name": name,
                        "tuned_model_name": f"{name}_tuned",
                        "best_score": result["best_score"],
                        "best_params": result["best_params"],
                        "search_type": result["search_type"],
                        "tuning_time": result["tuning_time"],
                    }
                )

        all_results.sort(key=lambda x: x["best_score"], reverse=True)

        return all_results[:top_n]

    def plot_comparison(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
        models_to_compare: Optional[List[str]] = None,
        output_file: Optional[str] = None,
    ):
        """
        Plot comparison between original and tuned models

        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            models_to_compare: List of model names to compare (None = all tuned)
            output_file: Optional file path to save plot
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        if not self.tuner.results:
            raise ValueError("No tuning results available. Run tune_models first.")

        all_models = self.automl.pipeline.registry.get_models()

        if models_to_compare is not None:
            model_names = [name for name in models_to_compare if name in all_models]
        else:
            model_names = [
                name
                for name in all_models.keys()
                if name in self.tuner.results or name.endswith("_tuned")
            ]

        original_models = []
        tuned_models = []

        for name in model_names:
            if name.endswith("_tuned"):
                tuned_models.append(name)
            elif f"{name}_tuned" in all_models:
                original_models.append(name)

        if not tuned_models:
            for name in model_names:
                if name in self.tuner.results:
                    original_models.append(name)
                    tuned_name = f"{name}_tuned"
                    if tuned_name in all_models:
                        tuned_models.append(tuned_name)

        results = []

        for name in original_models:
            if name in all_models:
                model = all_models[name]

                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

                if self.problem_type == "classification":
                    from sklearn.metrics import f1_score

                    train_score = f1_score(y_train, y_train_pred, average="weighted")
                    test_score = f1_score(y_test, y_test_pred, average="weighted")
                else:
                    from sklearn.metrics import r2_score

                    train_score = r2_score(y_train, y_train_pred)
                    test_score = r2_score(y_test, y_test_pred)

                results.append(
                    {
                        "model": name,
                        "type": "Original",
                        "train_score": train_score,
                        "test_score": test_score,
                        "gap": train_score - test_score,
                    }
                )

        for name in tuned_models:
            if name in all_models:
                model = all_models[name]

                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

                if self.problem_type == "classification":
                    from sklearn.metrics import f1_score

                    train_score = f1_score(y_train, y_train_pred, average="weighted")
                    test_score = f1_score(y_test, y_test_pred, average="weighted")
                else:
                    from sklearn.metrics import r2_score

                    train_score = r2_score(y_train, y_train_pred)
                    test_score = r2_score(y_test, y_test_pred)

                base_name = name.replace("_tuned", "")

                results.append(
                    {
                        "model": base_name,
                        "type": "Tuned",
                        "train_score": train_score,
                        "test_score": test_score,
                        "gap": train_score - test_score,
                    }
                )

        results_df = pd.DataFrame(results)

        if results_df.empty:
            raise ValueError("No models to compare")

        plt.figure(figsize=(12, 8))

        sns.set_style("whitegrid")

        ax = sns.barplot(
            x="model",
            y="test_score",
            hue="type",
            data=results_df,
            palette=["skyblue", "orange"],
        )

        for i, p in enumerate(ax.patches):
            ax.annotate(
                f"{p.get_height():.4f}",
                (p.get_x() + p.get_width() / 2.0, p.get_height()),
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=0,
            )

        plt.title("Model Performance Comparison: Original vs Tuned", fontsize=14)
        plt.xlabel("Model", fontsize=12)
        plt.ylabel("Test Score", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Model Type")
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
            logger.info(f"Comparison plot saved to {output_file}")

        plt.show()

        return results_df

    def add_to_automl_pipeline(self):
        """
        Add the tuning component directly to the AutoML pipeline for easier access
        """
        self.automl.pipeline.tuner = self.tuner

        def tune_models_method(
            automl_self,
            X,
            y,
            models_to_tune=None,
            search_type="random",
            n_iter=20,
            cv=5,
            register_best=True,
        ):
            return self.tune_models(
                X,
                y,
                models_to_tune=models_to_tune,
                search_type=search_type,
                n_iter=n_iter,
                cv=cv,
                register_best=register_best,
            )

        self.automl.tune_models = tune_models_method.__get__(self.automl)

        logger.info("Hyperparameter tuning capabilities added to AutoML instance")

        return self.automl
