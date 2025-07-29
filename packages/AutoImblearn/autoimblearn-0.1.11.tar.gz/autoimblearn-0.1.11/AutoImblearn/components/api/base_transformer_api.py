from .base_model_api import BaseModelAPI
from abc import abstractmethod


class BaseTransformerAPI(BaseModelAPI):
    """Abstract base class for sklearn-like transformers."""
    def fit(self, args, X_train, y_train, X_test, y_test):
        self.fit(args, X_train, y_train, X_test, y_test)
        result = self.transform(X_test)
        return result

    @abstractmethod
    def fit(self, args, X_train, y_train, X_test, y_test):
        pass

    @abstractmethod
    def transform(self, X):
        pass
