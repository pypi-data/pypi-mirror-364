"""
Pytest configuration and shared fixtures for AutoML Framework tests
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import shutil
import warnings
from sklearn.datasets import make_classification, make_regression, load_iris, load_wine
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture(scope="session")
def sample_classification_data():
    """Generate sample classification dataset"""
    X, y = make_classification(
        n_samples=200,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=2,
        random_state=42,
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture(scope="session")
def sample_regression_data():
    """Generate sample regression dataset"""
    X, y = make_regression(
        n_samples=200, n_features=10, n_informative=8, noise=0.1, random_state=42
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture(scope="session")
def multiclass_classification_data():
    """Generate multiclass classification dataset"""
    X, y = make_classification(
        n_samples=150,
        n_features=8,
        n_informative=6,
        n_redundant=1,
        n_classes=3,
        n_clusters_per_class=1,
        random_state=42,
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture(scope="session")
def iris_data():
    """Load iris dataset"""
    iris = load_iris()
    X_df = pd.DataFrame(iris.data, columns=iris.feature_names)
    y_series = pd.Series(iris.target, name="species")
    return X_df, y_series


@pytest.fixture(scope="session")
def wine_data():
    """Load wine dataset"""
    wine = load_wine()
    X_df = pd.DataFrame(wine.data, columns=wine.feature_names)
    y_series = pd.Series(wine.target, name="wine_class")
    return X_df, y_series


@pytest.fixture
def small_classification_data():
    """Generate small classification dataset for quick tests"""
    X, y = make_classification(
        n_samples=50,
        n_features=5,
        n_informative=3,
        n_redundant=1,
        n_classes=2,
        random_state=42,
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture
def overfitting_prone_data():
    """Generate dataset prone to overfitting (small sample, many features)"""
    X, y = make_classification(
        n_samples=50,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        n_classes=2,
        random_state=42,
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture
def sample_models():
    """Sample sklearn models for testing"""
    return {
        "RandomForest": RandomForestClassifier(n_estimators=10, random_state=42),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=100),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=10, random_state=42
        ),
        "LinearRegression": LinearRegression(),
    }


@pytest.fixture
def temp_directory():
    """Create temporary directory for testing file operations"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def automl_config():
    """Default AutoML configuration for testing"""
    return {"problem_type": "classification", "random_state": 42}


@pytest.fixture(scope="function")
def regression_config():
    """Regression AutoML configuration for testing"""
    return {"problem_type": "regression", "random_state": 42}


@pytest.fixture
def mock_training_data():
    """Mock training data with known properties"""
    np.random.seed(42)

    X = np.random.randn(100, 5)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(5)])
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture
def data_with_missing_values():
    """Dataset with missing values for testing preprocessing"""
    X, y = make_classification(n_samples=100, n_features=6, random_state=42)

    X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(6)])

    X_df.iloc[10:15, 1] = np.nan
    X_df.iloc[20:25, 3] = np.nan

    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture
def imbalanced_data():
    """Create imbalanced classification dataset"""
    X, y = make_classification(
        n_samples=200, n_features=8, n_classes=2, weights=[0.9, 0.1], random_state=42
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)
    y_series = pd.Series(y, name="target")

    return X_df, y_series


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test"""
    np.random.seed(42)

    import warnings
    from sklearn.exceptions import ConvergenceWarning, DataConversionWarning

    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    warnings.filterwarnings("ignore", category=DataConversionWarning)

    yield


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: mark test as slow-running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


class TestHelpers:
    """Helper functions for tests"""

    @staticmethod
    def assert_valid_predictions(predictions, y_true):
        """Assert that predictions are valid"""
        assert len(predictions) == len(y_true)
        assert not np.any(np.isnan(predictions))

    @staticmethod
    def assert_valid_probabilities(probabilities, y_true, n_classes=None):
        """Assert that probabilities are valid"""
        assert len(probabilities) == len(y_true)
        assert probabilities.shape[1] >= 2
        assert np.allclose(probabilities.sum(axis=1), 1.0)
        assert np.all(probabilities >= 0)
        assert np.all(probabilities <= 1)

        if n_classes is not None:
            assert probabilities.shape[1] == n_classes

    @staticmethod
    def assert_model_trained(model_wrapper):
        """Assert that a model wrapper is properly trained"""
        assert model_wrapper._is_fitted
        assert model_wrapper.training_log["fit_successful"]
        assert model_wrapper.training_log["training_duration"] is not None
        assert model_wrapper.training_log["training_duration"] > 0

    @staticmethod
    def assert_valid_leaderboard(leaderboard):
        """Assert that leaderboard has expected structure"""
        assert isinstance(leaderboard, pd.DataFrame)
        assert not leaderboard.empty
        assert "model" in leaderboard.columns

        metric_columns = [
            col
            for col in leaderboard.columns
            if any(metric in col.lower() for metric in ["accuracy", "f1", "r2", "mse"])
        ]
        assert len(metric_columns) > 0


@pytest.fixture
def test_helpers():
    """Provide test helper functions"""
    return TestHelpers
