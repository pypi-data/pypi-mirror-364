"""
Test suite for AutoML Framework

This package contains comprehensive tests for all components of the AutoML Framework.

Test Structure:
- test_automl.py: Main AutoML class tests
- test_pipeline.py: AutoML pipeline tests
- test_overfitting.py: Overfitting detection and mitigation tests
- test_hyperparameter_tuner.py: Hyperparameter tuning tests
- test_utils.py: Utility function tests
- test_model_wrapper.py: Model wrapper tests
- test_model_registry.py: Model registry tests
- test_preprocessors.py: Preprocessor tests
- test_metrics.py: Metrics calculator tests
- conftest.py: Shared test configuration and fixtures

Usage:
    Run all tests:
    >>> pytest tests/

    Run specific test file:
    >>> pytest tests/test_automl.py

    Run with coverage:
    >>> pytest tests/ --cov=automl --cov-report=html
"""

__version__ = "0.1.0"
__test_suite__ = "AutoML Framework Test Suite"
