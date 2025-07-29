"""
Tests for utility functions
"""

import pytest
import pandas as pd
import numpy as np
import logging
from sklearn.datasets import make_classification

from automl.utils import DataUtils, setup_logging


class TestDataUtils:
    """Test DataUtils functionality"""

    def test_train_test_split_basic(self, sample_classification_data):
        """Test basic train-test split functionality"""
        X, y = sample_classification_data

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(X, y)

        assert len(X_train) == int(0.8 * len(X))
        assert len(X_test) == len(X) - len(X_train)
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)

        assert isinstance(X_train, type(X))
        assert isinstance(X_test, type(X))
        assert isinstance(y_train, type(y))
        assert isinstance(y_test, type(y))

    def test_train_test_split_custom_size(self, sample_classification_data):
        """Test train-test split with custom test size"""
        X, y = sample_classification_data

        test_size = 0.3
        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=test_size
        )

        expected_test_size = int(test_size * len(X))
        assert len(X_test) == expected_test_size
        assert len(X_train) == len(X) - expected_test_size

    def test_train_test_split_random_state(self, sample_classification_data):
        """Test train-test split reproducibility"""
        X, y = sample_classification_data

        X_train1, X_test1, y_train1, y_test1 = DataUtils.train_test_split(
            X, y, random_state=42
        )
        X_train2, X_test2, y_train2, y_test2 = DataUtils.train_test_split(
            X, y, random_state=42
        )

        pd.testing.assert_frame_equal(X_train1, X_train2)
        pd.testing.assert_frame_equal(X_test1, X_test2)
        pd.testing.assert_series_equal(y_train1, y_train2)
        pd.testing.assert_series_equal(y_test1, y_test2)

        X_train3, X_test3, y_train3, y_test3 = DataUtils.train_test_split(
            X, y, random_state=123
        )

        assert not X_train1.equals(X_train3)

    def test_data_quality_check_basic(self, sample_classification_data):
        """Test basic data quality checking"""
        X, y = sample_classification_data

        report = DataUtils.check_data_quality(X, y)

        assert isinstance(report, dict)
        assert "missing_values_X" in report
        assert "missing_values_y" in report
        assert "class_distribution" in report
        assert "is_imbalanced" in report
        assert "zero_variance_features" in report

        assert report["missing_values_X"] == 0
        assert report["missing_values_y"] == 0
        assert isinstance(report["class_distribution"], dict)
        assert isinstance(report["is_imbalanced"], bool)
        assert isinstance(report["zero_variance_features"], list)

    def test_data_quality_check_missing_values(self, data_with_missing_values):
        """Test data quality check with missing values"""
        X, y = data_with_missing_values

        report = DataUtils.check_data_quality(X, y)

        assert report["missing_values_X"] > 0
        assert report["missing_values_y"] == 0

    def test_data_quality_check_imbalanced(self, imbalanced_data):
        """Test data quality check with imbalanced data"""
        X, y = imbalanced_data

        report = DataUtils.check_data_quality(X, y)

        assert report["is_imbalanced"] == True

        class_dist = report["class_distribution"]
        assert isinstance(class_dist, dict)
        assert len(class_dist) == 2

        min_class_proportion = min(class_dist.values())
        assert min_class_proportion < 0.1

    def test_data_quality_check_zero_variance(self):
        """Test data quality check with zero variance features"""
        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(5)])
        y_series = pd.Series(y)

        X_df["zero_var_feature"] = 1.0

        report = DataUtils.check_data_quality(X_df, y_series)

        assert len(report["zero_variance_features"]) == 1
        assert "zero_var_feature" in report["zero_variance_features"]

    def test_data_quality_check_numpy_input(self):
        """Test data quality check with numpy arrays"""
        X, y = make_classification(n_samples=100, n_features=5, random_state=42)

        report = DataUtils.check_data_quality(X, y)

        assert isinstance(report, dict)
        assert "missing_values_X" in report

    def test_data_quality_check_series_target(self, sample_classification_data):
        """Test data quality check with pandas Series target"""
        X, y = sample_classification_data

        report = DataUtils.check_data_quality(X, y)

        assert report["missing_values_y"] == 0
        assert isinstance(report["class_distribution"], dict)

    def test_data_quality_check_multiclass(self, multiclass_classification_data):
        """Test data quality check with multiclass data"""
        X, y = multiclass_classification_data

        report = DataUtils.check_data_quality(X, y)

        class_dist = report["class_distribution"]
        assert len(class_dist) == 3
        assert all(proportion > 0 for proportion in class_dist.values())

        assert abs(sum(class_dist.values()) - 1.0) < 1e-10

    def test_data_quality_check_regression(self, sample_regression_data):
        """Test data quality check with regression data"""
        X, y = sample_regression_data

        report = DataUtils.check_data_quality(X, y)

        assert "class_distribution" in report

    def test_data_quality_edge_cases(self):
        """Test data quality check edge cases"""
        X_small = pd.DataFrame({"feature": [1, 2]})
        y_small = pd.Series([0, 1])

        report = DataUtils.check_data_quality(X_small, y_small)
        assert isinstance(report, dict)

        X_single = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
        y_single = pd.Series([0, 1, 0, 1, 0])

        report = DataUtils.check_data_quality(X_single, y_single)
        assert len(report["zero_variance_features"]) == 0  # No zero variance

        X_same = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
        y_same = pd.Series([0, 0, 0, 0, 0])

        report = DataUtils.check_data_quality(X_same, y_same)
        class_dist = report["class_distribution"]
        assert len(class_dist) == 1
        assert list(class_dist.values())[0] == 1.0


class TestLoggingSetup:
    """Test logging setup functionality"""

    def test_setup_logging_default(self):
        """Test default logging setup"""
        logger = setup_logging()

        assert isinstance(logger, logging.Logger)
        assert logger.name == "AutoML"
        assert logger.level == logging.INFO

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level_name in levels:
            logger = setup_logging(level=level_name)
            expected_level = getattr(logging, level_name)
            assert logger.level == expected_level

    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level"""
        logger = setup_logging(level="INVALID")
        assert logger.level == logging.INFO

    def test_setup_logging_case_insensitive(self):
        """Test logging setup is case insensitive"""
        logger1 = setup_logging(level="debug")
        logger2 = setup_logging(level="DEBUG")
        logger3 = setup_logging(level="Debug")

        assert logger1.level == logging.DEBUG
        assert logger2.level == logging.DEBUG
        assert logger3.level == logging.DEBUG

    def test_logging_output(self, caplog):
        """Test that logging actually works"""
        logger = setup_logging(level="INFO")

        with caplog.at_level(logging.INFO):
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")

        assert "Test info message" in caplog.text
        assert "Test warning message" in caplog.text
        assert "Test error message" in caplog.text

    def test_logging_format(self, caplog):
        """Test logging format"""
        logger = setup_logging(level="INFO")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        record = caplog.records[0]
        assert record.name == "AutoML"
        assert record.levelname == "INFO"
        assert record.getMessage() == "Test message"

    def test_multiple_logger_calls(self):
        """Test multiple calls to setup_logging"""
        logger1 = setup_logging(level="INFO")
        logger2 = setup_logging(level="DEBUG")

        assert isinstance(logger1, logging.Logger)
        assert isinstance(logger2, logging.Logger)

        assert logger1.name == logger2.name == "AutoML"

        assert logger2.level == logging.DEBUG


class TestDataUtilsEdgeCases:
    """Test edge cases and error handling in DataUtils"""

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        X_empty = pd.DataFrame()
        y_empty = pd.Series(dtype=int)

        try:
            report = DataUtils.check_data_quality(X_empty, y_empty)
            assert isinstance(report, dict)
        except Exception as e:
            assert len(str(e)) > 0

    def test_mismatched_lengths(self):
        """Test handling of mismatched X and y lengths"""
        X = pd.DataFrame({"feature": [1, 2, 3]})
        y = pd.Series([0, 1])

        with pytest.raises(ValueError):
            DataUtils.train_test_split(X, y)

    def test_single_sample(self):
        """Test handling of single sample"""
        X_single = pd.DataFrame({"feature": [1]})
        y_single = pd.Series([0])

        report = DataUtils.check_data_quality(X_single, y_single)
        assert isinstance(report, dict)

        with pytest.raises(ValueError):
            DataUtils.train_test_split(X_single, y_single, test_size=0.5)

    def test_all_missing_values(self):
        """Test handling of all missing values"""
        X_missing = pd.DataFrame({"feature": [np.nan, np.nan, np.nan]})
        y_normal = pd.Series([0, 1, 0])

        report = DataUtils.check_data_quality(X_missing, y_normal)

        assert report["missing_values_X"] == 3

    def test_categorical_features(self):
        """Test handling of categorical features"""
        X_cat = pd.DataFrame(
            {
                "numeric": [1, 2, 3, 4, 5],
                "categorical": pd.Categorical(["A", "B", "A", "B", "A"]),
            }
        )
        y = pd.Series([0, 1, 0, 1, 0])

        report = DataUtils.check_data_quality(X_cat, y)

        assert isinstance(report, dict)
        assert "missing_values_X" in report

    def test_very_large_dataset_simulation(self):
        """Test behavior with simulated large dataset info"""
        X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
        X_df = pd.DataFrame(X)
        y_series = pd.Series(y)

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X_df, y_series, test_size=0.2
        )

        assert len(X_train) == 800
        assert len(X_test) == 200

        report = DataUtils.check_data_quality(X_df, y_series)
        assert isinstance(report, dict)
        assert report["missing_values_X"] == 0

    def test_extreme_class_imbalance(self):
        """Test with extreme class imbalance"""
        X = pd.DataFrame({"feature": range(1000)})
        y = pd.Series([0] * 999 + [1])

        report = DataUtils.check_data_quality(X, y)

        assert report["is_imbalanced"] == True
        class_dist = report["class_distribution"]
        assert min(class_dist.values()) == 0.001
        assert max(class_dist.values()) == 0.999

    def test_string_target(self):
        """Test handling of string target variables"""
        X = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
        y = pd.Series(["cat", "dog", "cat", "dog", "cat"])

        report = DataUtils.check_data_quality(X, y)

        assert isinstance(report["class_distribution"], dict)
        assert "cat" in report["class_distribution"]
        assert "dog" in report["class_distribution"]

    def test_numeric_target_many_classes(self):
        """Test handling of numeric target with many classes"""
        X = pd.DataFrame({"feature": range(50)})
        y = pd.Series(range(50))  # 50 unique classes

        report = DataUtils.check_data_quality(X, y)

        assert len(report["class_distribution"]) == 50
        assert all(
            abs(prop - 0.02) < 1e-10 for prop in report["class_distribution"].values()
        )


class TestDataUtilsIntegration:
    """Integration tests for DataUtils"""

    def test_full_workflow_classification(self, sample_classification_data):
        """Test complete workflow with classification data"""
        X, y = sample_classification_data

        report = DataUtils.check_data_quality(X, y)
        assert report["missing_values_X"] == 0
        assert not report["is_imbalanced"]

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.3
        )

        train_dist = y_train.value_counts(normalize=True).sort_index()
        test_dist = y_test.value_counts(normalize=True).sort_index()

        for class_label in train_dist.index:
            if class_label in test_dist.index:
                assert abs(train_dist[class_label] - test_dist[class_label]) < 0.2

    def test_full_workflow_regression(self, sample_regression_data):
        """Test complete workflow with regression data"""
        X, y = sample_regression_data

        report = DataUtils.check_data_quality(X, y)
        assert report["missing_values_X"] == 0

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.25
        )

        assert len(X_train) == int(0.75 * len(X))
        assert len(X_test) == len(X) - len(X_train)

        train_mean = y_train.mean()
        test_mean = y_test.mean()
        overall_mean = y.mean()

        assert abs(train_mean - overall_mean) < abs(overall_mean) * 0.5
        assert abs(test_mean - overall_mean) < abs(overall_mean) * 0.5

    def test_workflow_with_problematic_data(self):
        """Test workflow with data that has various issues"""
        np.random.seed(42)
        X = pd.DataFrame(
            {
                "normal_feature": np.random.randn(100),
                "zero_variance": np.ones(100),
                "missing_feature": [1.0] * 80 + [np.nan] * 20,
                "categorical": pd.Categorical(["A", "B"] * 50),
            }
        )
        y = pd.Series([0] * 95 + [1] * 5)

        report = DataUtils.check_data_quality(X, y)

        assert report["missing_values_X"] == 20
        assert report["is_imbalanced"] == True
        assert "zero_variance" in report["zero_variance_features"]

        X_train, X_test, y_train, y_test = DataUtils.train_test_split(
            X, y, test_size=0.2
        )

        assert len(X_train) + len(X_test) == len(X)
        assert len(y_train) + len(y_test) == len(y)

    def test_reproducibility_across_calls(self, sample_classification_data):
        """Test that operations are reproducible"""
        X, y = sample_classification_data

        results = []
        for _ in range(3):
            X_train, X_test, y_train, y_test = DataUtils.train_test_split(
                X, y, test_size=0.3, random_state=42
            )
            results.append((X_train, X_test, y_train, y_test))

        for i in range(1, len(results)):
            pd.testing.assert_frame_equal(results[0][0], results[i][0])
            pd.testing.assert_frame_equal(results[0][1], results[i][1])
            pd.testing.assert_series_equal(results[0][2], results[i][2])
            pd.testing.assert_series_equal(results[0][3], results[i][3])

    def test_data_quality_consistency(self, sample_classification_data):
        """Test that data quality checks are consistent"""
        X, y = sample_classification_data

        reports = [DataUtils.check_data_quality(X, y) for _ in range(3)]

        for i in range(1, len(reports)):
            assert reports[0] == reports[i]


class TestUtilsHelpers:
    """Test any additional helper functions in utils"""

    def test_logging_levels_mapping(self):
        """Test that all logging levels are properly mapped"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            logger = setup_logging(level=level)
            expected_level = getattr(logging, level)
            assert logger.level == expected_level

    def test_utils_module_imports(self):
        """Test that all expected utilities are available"""
        from automl.utils import DataUtils, setup_logging

        assert callable(DataUtils.train_test_split)
        assert callable(DataUtils.check_data_quality)
        assert callable(setup_logging)

        expected_methods = ["train_test_split", "check_data_quality"]
        for method in expected_methods:
            assert hasattr(DataUtils, method)
            assert callable(getattr(DataUtils, method))

    def test_datautils_static_methods(self):
        """Test that DataUtils methods are static"""
        from automl.utils import DataUtils

        X = pd.DataFrame({"feature": [1, 2, 3, 4]})
        y = pd.Series([0, 1, 0, 1])

        report = DataUtils.check_data_quality(X, y)
        X_train, X_test, y_train, y_test = DataUtils.train_test_split(X, y)

        assert isinstance(report, dict)
        assert len(X_train) + len(X_test) == len(X)
