"""
Examples and demonstrations for AutoML Framework

This package contains various examples showing how to use the AutoML Framework
for different use cases and scenarios.

Available Examples:
- basic_usage: Simple getting started examples
- advanced_example: Advanced features and customization
- run_automl: One-line AutoML execution for quick results

Usage:
    You can run examples directly:

    >>> python examples/basic_usage.py
    >>> python examples/run_automl.py

    Or import functions from examples:

    >>> from examples.run_automl import run_automl
    >>> from examples.basic_usage import example_with_synthetic_data
"""

try:
    from .run_automl import run_automl
    from .basic_usage import (
        example_with_synthetic_data,
        example_with_wine_dataset,
        example_with_overfitting_analysis,
    )

    __all__ = [
        "run_automl",
        "example_with_synthetic_data",
        "example_with_wine_dataset",
        "example_with_overfitting_analysis",
    ]

except ImportError as e:
    import warnings

    warnings.warn(
        f"Some example functions may not be available due to missing dependencies: {e}"
    )
    __all__ = []

__version__ = "0.1.0"
__author__ = "AutoML Framework Team"
__description__ = "Examples and demonstrations for AutoML Framework"
