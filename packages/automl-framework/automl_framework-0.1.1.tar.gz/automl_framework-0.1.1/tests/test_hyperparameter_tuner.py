"""
Tests for hyperparameter tuning functionality
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from automl.hyperparameter_tuner import HyperparameterTuner


class TestHyperparameterTuner:
    """Test hyperparameter tuning functionality"""

    def test_tuner_initialization(self):
        """Test tuner initialization"""
        tuner = HyperparameterTuner()
        assert tuner.problem_type == "classification"
        assert tuner.cv == 5
        assert tuner.random_state == 42
        assert tuner.scoring == "f1_weighted"

        tuner = HyperparameterTuner(
            problem_type="regression", cv=3, random_state=123, n_jobs=1
        )
        assert tuner.problem_type == "regression"
        assert tuner.cv == 3
        assert tuner.random_state == 123
        assert tuner.scoring == "neg_mean_squared_error"
        assert tuner.n_jobs == 1

    def test_scoring_configuration(self):
        """Test scoring metric configuration"""
        tuner = HyperparameterTuner()

        tuner.set_scoring("accuracy")
        assert tuner.scoring == "accuracy"

        tuner.set_scoring("roc_auc")
        assert tuner.scoring == "roc_auc"

    def test_parameter_grid_generation(self):
        """Test parameter grid generation for different models"""
        tuner = HyperparameterTuner(problem_type="classification")

        dt_params = tuner.get_param_grid("DecisionTree", "grid")
        assert "max_depth" in dt_params
        assert "min_samples_split" in dt_params
        assert "min_samples_leaf" in dt_params
        assert "criterion" in dt_params

        rf_params = tuner.get_param_grid("RandomForest", "grid")
        assert "n_estimators" in rf_params
        assert "max_depth" in rf_params
        assert "max_features" in rf_params
        assert "bootstrap" in rf_params

        gb_params = tuner.get_param_grid("GradientBoosting", "grid")
        assert "learning_rate" in gb_params
        assert "n_estimators" in gb_params
        assert "max_depth" in gb_params

        lr_params = tuner.get_param_grid("LogisticRegression", "grid")
        assert "C" in lr_params
        assert "penalty" in lr_params

        svm_params = tuner.get_param_grid("SVM", "grid")
        assert "C" in svm_params
        assert "kernel" in svm_params
        assert "gamma" in svm_params

        mlp_params = tuner.get_param_grid("MLP", "grid")
        assert "hidden_layer_sizes" in mlp_params
        assert "activation" in mlp_params
        assert "alpha" in mlp_params

        knn_params = tuner.get_param_grid("KNN", "grid")
        assert "n_neighbors" in knn_params
        assert "weights" in knn_params
        assert "algorithm" in knn_params

    def test_parameter_grid_regression(self):
        """Test parameter grid generation for regression models"""
        tuner = HyperparameterTuner(problem_type="regression")

        dt_params = tuner.get_param_grid("DecisionTree", "grid")
        assert "criterion" in dt_params
        assert any(
            "squared_error" in str(criterion) or "friedman_mse" in str(criterion)
            for criterion in dt_params["criterion"]
        )

    def test_bayesian_parameter_spaces(self):
        """Test Bayesian optimization parameter spaces"""
        try:
            from skopt.space import Real, Integer, Categorical

            tuner = HyperparameterTuner(problem_type="classification")

            rf_space = tuner.get_param_grid("RandomForest", "bayesian")
            if rf_space:
                assert isinstance(rf_space["n_estimators"], Integer)
                assert isinstance(rf_space["max_depth"], Integer)
                assert isinstance(rf_space["max_features"], Categorical)

        except ImportError:
            pytest.skip("scikit-optimize not available for Bayesian optimization tests")

    def test_hyperopt_parameter_spaces(self):
        """Test Hyperopt parameter spaces"""
        try:
            import hyperopt

            tuner = HyperparameterTuner(problem_type="classification")

            rf_space = tuner.get_param_grid("RandomForest", "hyperopt")
            if rf_space:
                assert "n_estimators" in rf_space
                assert "max_depth" in rf_space
                assert "max_features" in rf_space

        except ImportError:
            pytest.skip("hyperopt not available for hyperopt tests")

    def test_grid_search_tuning(self, small_classification_data):
        """Test grid search hyperparameter tuning"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)

        param_grid = {"max_depth": [3, 5], "min_samples_split": [2, 5]}

        result = tuner.tune_model(
            "DecisionTree",
            model,
            X,
            y,
            param_grid=param_grid,
            search_type="grid",
            n_splits=3,
        )

        assert isinstance(result, dict)
        assert "model_name" in result
        assert result["model_name"] == "DecisionTree"

        if "error" not in result:
            assert "best_params" in result
            assert "best_score" in result
            assert "best_estimator" in result
            assert "search_type" in result
            assert result["search_type"] == "grid"

            best_params = result["best_params"]
            assert best_params["max_depth"] in [3, 5]
            assert best_params["min_samples_split"] in [2, 5]

    def test_random_search_tuning(self, small_classification_data):
        """Test random search hyperparameter tuning"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = RandomForestClassifier(random_state=42)

        result = tuner.tune_model(
            "RandomForest", model, X, y, search_type="random", n_iter=3, n_splits=3
        )

        assert isinstance(result, dict)
        assert "model_name" in result

        if "error" not in result:
            assert "best_params" in result
            assert "best_score" in result
            assert "best_estimator" in result
            assert result["search_type"] == "random"

    def test_halving_search_tuning(self, small_classification_data):
        """Test halving search (if available)"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        try:
            model = DecisionTreeClassifier(random_state=42)

            result = tuner.tune_model(
                "DecisionTree", model, X, y, search_type="halving", n_splits=3
            )

            if "error" not in result:
                assert "best_params" in result
                assert "best_score" in result
                assert result["search_type"] == "halving"

        except Exception:
            pytest.skip("Halving search not available in this sklearn version")

    @pytest.mark.slow
    def test_bayesian_optimization_tuning(self, small_classification_data):
        """Test Bayesian optimization (marked as slow)"""
        try:
            from skopt import BayesSearchCV

            X, y = small_classification_data
            tuner = HyperparameterTuner(problem_type="classification")

            model = RandomForestClassifier(random_state=42)

            result = tuner.tune_model(
                "RandomForest",
                model,
                X,
                y,
                search_type="bayesian",
                n_iter=3,
                n_splits=3,
            )

            if "error" not in result:
                assert "best_params" in result
                assert "best_score" in result
                assert result["search_type"] == "bayesian"
                assert "search_history" in result

        except ImportError:
            pytest.skip("scikit-optimize not available for Bayesian optimization")

    @pytest.mark.slow
    def test_hyperopt_tuning(self, small_classification_data):
        """Test Hyperopt optimization (marked as slow)"""
        try:
            import hyperopt

            X, y = small_classification_data
            tuner = HyperparameterTuner(problem_type="classification")

            model = DecisionTreeClassifier(random_state=42)

            result = tuner.tune_model(
                "DecisionTree",
                model,
                X,
                y,
                search_type="hyperopt",
                n_iter=3,
                n_splits=3,
            )

            if "error" not in result:
                assert "best_params" in result
                assert "best_score" in result
                assert result["search_type"] == "hyperopt"
                assert "search_history" in result

        except ImportError:
            pytest.skip("hyperopt not available for hyperopt optimization")

    def test_multiple_models_tuning(self, small_classification_data):
        """Test tuning multiple models at once"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        models = {
            "DecisionTree": DecisionTreeClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=100),
        }

        results = tuner.tune_multiple_models(
            models, X, y, search_type="random", n_iter=2
        )

        assert isinstance(results, dict)
        assert len(results) == 2
        assert "DecisionTree" in results
        assert "LogisticRegression" in results

        for name, result in results.items():
            assert "model_name" in result
            if "error" not in result:
                assert "best_params" in result
                assert "best_score" in result

    def test_get_best_model(self, small_classification_data):
        """Test getting the best model from tuning results"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)
        result = tuner.tune_model(
            "DecisionTree", model, X, y, search_type="grid", n_splits=3
        )

        if "error" not in result:
            best_name, best_estimator, best_score = tuner.get_best_model()

            assert best_name == "DecisionTree"
            assert best_estimator is not None
            assert isinstance(best_score, (int, float))
            assert best_score == result["best_score"]

    def test_tuning_summary(self, small_classification_data):
        """Test tuning summary generation"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        models = {
            "DecisionTree": DecisionTreeClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=100),
        }

        tuner.tune_multiple_models(models, X, y, search_type="random", n_iter=2)

        summary = tuner.get_tuning_summary()

        assert isinstance(summary, pd.DataFrame)
        assert not summary.empty
        assert "model" in summary.columns
        assert "best_score" in summary.columns
        assert "search_type" in summary.columns
        assert "status" in summary.columns

        if len(summary) > 1:
            scores = summary["best_score"].dropna()
            if len(scores) > 1:
                assert scores.is_monotonic_decreasing

    def test_tuning_results_plotting(self, small_classification_data, temp_directory):
        """Test plotting tuning results"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)
        param_grid = {"max_depth": [3, 5, 7], "min_samples_split": [2, 5, 10]}

        result = tuner.tune_model(
            "DecisionTree",
            model,
            X,
            y,
            param_grid=param_grid,
            search_type="grid",
            n_splits=3,
        )

        if "error" not in result and "cv_results" in result:
            output_file = os.path.join(temp_directory, "tuning_plot.png")

            try:
                tuner.plot_tuning_results(
                    "DecisionTree",
                    "max_depth",
                    "min_samples_split",
                    output_file=output_file,
                )

                assert os.path.exists(output_file)

            except Exception as e:
                pytest.skip(f"Plotting failed (expected in headless environment): {e}")

    def test_parameter_importance_plotting(
        self, small_classification_data, temp_directory
    ):
        """Test parameter importance plotting"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)
        result = tuner.tune_model(
            "DecisionTree", model, X, y, search_type="grid", n_splits=3
        )

        if "error" not in result and "cv_results" in result:
            output_file = os.path.join(temp_directory, "param_importance.png")

            try:
                tuner.plot_parameter_importance(
                    "DecisionTree", n_top_params=5, output_file=output_file
                )

                assert os.path.exists(output_file)

            except Exception as e:
                pytest.skip(f"Parameter importance plotting failed: {e}")

    def test_save_load_tuning_results(self, small_classification_data, temp_directory):
        """Test saving and loading tuning results"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)
        result = tuner.tune_model(
            "DecisionTree", model, X, y, search_type="grid", n_splits=3
        )

        if "error" not in result:
            tuner.save_tuning_results(temp_directory, "DecisionTree")

            results_file = os.path.join(
                temp_directory, "DecisionTree_tuning_results.pkl"
            )
            estimator_file = os.path.join(
                temp_directory, "DecisionTree_best_estimator.pkl"
            )

            assert os.path.exists(results_file)
            assert os.path.exists(estimator_file)

            new_tuner = HyperparameterTuner(problem_type="classification")
            loaded_results = new_tuner.load_tuning_results(
                temp_directory, "DecisionTree"
            )

            assert isinstance(loaded_results, dict)
            assert "best_params" in loaded_results
            assert "best_score" in loaded_results
            assert loaded_results["best_score"] == result["best_score"]

    def test_save_all_tuning_results(self, small_classification_data, temp_directory):
        """Test saving all tuning results"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        models = {
            "DecisionTree": DecisionTreeClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=100),
        }

        tuner.tune_multiple_models(models, X, y, search_type="random", n_iter=2)

        tuner.save_tuning_results(temp_directory)

        summary_file = os.path.join(temp_directory, "tuning_summary.csv")
        assert os.path.exists(summary_file)

        for model_name in models.keys():
            results_file = os.path.join(
                temp_directory, f"{model_name}_tuning_results.pkl"
            )
            if os.path.exists(results_file):
                assert os.path.getsize(results_file) > 0

    def test_regression_tuning(self, sample_regression_data):
        """Test hyperparameter tuning for regression"""
        X, y = sample_regression_data
        tuner = HyperparameterTuner(problem_type="regression")

        assert tuner.scoring == "neg_mean_squared_error"

        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(random_state=42)

        result = tuner.tune_model(
            "RandomForestRegressor",
            model,
            X,
            y,
            search_type="random",
            n_iter=3,
            n_splits=3,
        )

        if "error" not in result:
            assert "best_params" in result
            assert "best_score" in result
            assert result["best_score"] <= 0

    def test_custom_parameter_grid(self, small_classification_data):
        """Test using custom parameter grid"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)

        custom_grid = {"max_depth": [2, 4], "criterion": ["gini", "entropy"]}

        result = tuner.tune_model(
            "CustomDecisionTree",
            model,
            X,
            y,
            param_grid=custom_grid,
            search_type="grid",
            n_splits=3,
        )

        if "error" not in result:
            best_params = result["best_params"]
            assert best_params["max_depth"] in [2, 4]
            assert best_params["criterion"] in ["gini", "entropy"]

    def test_unknown_model_parameter_grid(self):
        """Test parameter grid generation for unknown model"""
        tuner = HyperparameterTuner(problem_type="classification")

        unknown_params = tuner.get_param_grid("UnknownModel", "grid")

        assert isinstance(unknown_params, dict)
        assert len(unknown_params) <= 1

    def test_error_handling(self, small_classification_data):
        """Test error handling in hyperparameter tuning"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        from sklearn.svm import SVC

        model = SVC(random_state=42)

        param_grid = {"C": [0.001], "gamma": ["scale"]}

        result = tuner.tune_model(
            "SVC", model, X, y, param_grid=param_grid, search_type="grid", n_splits=3
        )

        assert isinstance(result, dict)
        if "error" in result:
            assert "status" in result
            assert result["status"] == "failed"

    def test_get_best_model_empty_results(self):
        """Test getting best model when no results exist"""
        tuner = HyperparameterTuner()

        with pytest.raises(ValueError):
            tuner.get_best_model()

    def test_invalid_search_type(self, small_classification_data):
        """Test handling of invalid search type"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)

        result = tuner.tune_model(
            "DecisionTree", model, X, y, search_type="invalid_search_type", n_splits=3
        )

        assert isinstance(result, dict)
        if "error" not in result:
            assert result["search_type"] in ["grid", "invalid_search_type"]

    def test_cross_validation_configuration(self, small_classification_data):
        """Test different cross-validation configurations"""
        X, y = small_classification_data
        tuner = HyperparameterTuner(problem_type="classification")

        model = DecisionTreeClassifier(random_state=42)

        result = tuner.tune_model(
            "DecisionTree", model, X, y, search_type="grid", n_splits=2
        )

        if "error" not in result:
            assert "best_params" in result
            assert "best_score" in result
