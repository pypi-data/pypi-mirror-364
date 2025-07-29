"""
Preprocessors for the AutoML framework.
Contains abstract base class and common implementations.
"""

from abc import ABC, abstractmethod
from sklearn.preprocessing import StandardScaler


class Preprocessor(ABC):
    """Abstract base class for data preprocessors"""

    @abstractmethod
    def fit(self, X, y=None):
        """Fit the preprocessor to the data"""
        pass

    @abstractmethod
    def transform(self, X):
        """Transform the data"""
        pass

    def fit_transform(self, X, y=None):
        """Fit to data, then transform it"""
        self.fit(X, y)
        return self.transform(X)


class StandardPreprocessor(Preprocessor):
    """Standard scaler preprocessor"""

    def __init__(self):
        self.scaler = StandardScaler()

    def fit(self, X, y=None):
        """Fit the standard scaler to the data"""
        self.scaler.fit(X)
        return self

    def transform(self, X):
        """Transform the data using the fitted scaler"""
        return self.scaler.transform(X)
