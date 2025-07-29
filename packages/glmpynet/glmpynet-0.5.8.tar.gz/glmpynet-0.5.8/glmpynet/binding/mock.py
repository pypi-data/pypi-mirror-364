import numpy as np
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
from .base import GlmNetBinding
from typing import Dict, Any


class MockGlmNetBinding(GlmNetBinding):
    """
    A mock implementation of the GlmNetBinding interface for testing.

    This class uses scikit-learn's LogisticRegression under the hood to
    simulate the behavior of the real glmnet C++ engine.
    """

    def fit(
            self,
            x: np.ndarray,
            y: np.ndarray,
            alpha: float,
            nlambda: int,
    ) -> Dict[str, Any]:
        """
        Simulates a call to the glmnet solver using scikit-learn.
        """
        penalty = 'l1' if alpha == 1.0 else 'l2'

        # The 'saga' solver is stochastic. Providing a fixed random_state
        # ensures that it is deterministic, which is required to pass
        # scikit-learn's idempotency checks.
        sklearn_model = SklearnLogisticRegression(
            penalty=penalty,
            C=1e5,
            solver='saga',
            tol=1e-4,
            max_iter=1000,
            random_state=42  # Make the solver deterministic
        )

        sklearn_model.fit(x, y)

        intercept_vector = np.full(nlambda, sklearn_model.intercept_[0])
        coefficient_matrix = np.tile(sklearn_model.coef_.T, (1, nlambda))

        return {
            'a0': intercept_vector,
            'ca': coefficient_matrix,
            'n_passes': 100,
            'jerr': 0,
        }
