"""
Utility functions for the AutoML framework.
Provides helper functions for data manipulation and analysis.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


class DataUtils:
    """Utility functions for data manipulation"""

    @staticmethod
    def train_test_split(X, y, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    @staticmethod
    def check_data_quality(X, y):
        """Check data quality and return a report"""
        report = {}

        report["missing_values_X"] = X.isnull().sum().sum()
        if isinstance(y, pd.Series) or isinstance(y, pd.DataFrame):
            report["missing_values_y"] = y.isnull().sum().sum()

        if isinstance(y, pd.Series) or isinstance(y, np.ndarray):
            value_counts = pd.Series(y).value_counts(normalize=True)
            report["class_distribution"] = value_counts.to_dict()
            report["is_imbalanced"] = (value_counts < 0.1).any()

        if isinstance(X, pd.DataFrame):
            zero_var_features = X.columns[X.var() == 0].tolist()
            report["zero_variance_features"] = zero_var_features

        return report


def setup_logging(level="INFO"):
    """Set up logging configuration"""
    import logging

    logging_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = logging_levels.get(level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    return logging.getLogger("AutoML")
