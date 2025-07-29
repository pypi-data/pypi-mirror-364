"""
AutoML Framework

A modular framework for automated machine learning.
"""

from .utils import DataUtils, setup_logging
from .automl import AutoML
from .hyperparameter_tuner import HyperparameterTuner
from .automl_integration import TuningIntegrator

from .__version__ import (
    __version__,
    __author__,
    __email__,
    __description__,
)

__all__ = [
    "AutoML",
    "DataUtils",
    "setup_logging",
    "HyperparameterTuner",
    "TuningIntegrator",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
