"""
Main script for the AutoML framework.
Demonstrates usage of the framework.
"""

import os
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier

from automl import AutoML
from .automl.utils import DataUtils, setup_logging


def main():
    """Main function to demonstrate AutoML functionality"""
    logger = setup_logging(level="INFO")
    logger.info("Starting AutoML demonstration")

    data_path = "fraud/data/data_train_fraud.csv"

    if not os.path.exists(data_path):
        logger.warning(f"Data file not found: {data_path}")
        logger.info("Using sample iris dataset for demonstration")
        from sklearn.datasets import load_iris

        iris = load_iris()
        X = pd.DataFrame(iris.data, columns=iris.feature_names)
        y = pd.Series(iris.target)
    else:
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        X = df.drop(columns="flag_kena_fraud")
        y = df["flag_kena_fraud"]

    logger.info("Checking data quality")
    data_report = DataUtils.check_data_quality(X, y)
    logger.info(f"Data quality report: {data_report}")

    logger.info("Splitting data into train and test sets")
    X_train, X_test, y_train, y_test = DataUtils.train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info("Creating AutoML instance")
    config = {
        "problem_type": "classification",
        "random_state": 42,
    }

    automl = AutoML(config)

    logger.info("Registering additional models")
    automl.register_model("AdaBoost", AdaBoostClassifier(random_state=42))

    logger.info("Training models")
    automl.fit(X_train, y_train)

    logger.info("Evaluating models")
    results = automl.evaluate(X_test, y_test)

    logger.info("Model Leaderboard:")
    leaderboard = automl.get_leaderboard()
    print(leaderboard)

    logger.info("Making predictions with best model")
    predictions = automl.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    logger.info(f"Accuracy of best model: {accuracy:.4f}")

    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)

    logger.info("Saving best model")
    automl.save_best_model(os.path.join(model_dir, "best_model.pkl"))

    logger.info("AutoML demonstration completed")


if __name__ == "__main__":
    main()
