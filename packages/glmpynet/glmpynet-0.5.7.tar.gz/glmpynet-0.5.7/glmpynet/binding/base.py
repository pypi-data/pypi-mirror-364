from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np

class GlmNetBinding(ABC):
    """
    Abstract Base Class for the glmnet C++ binding.

    This class defines the interface that the high-level scikit-learn
    compatible API will use to interact with the underlying C++ solver.
    Any implementation of this class (whether a real C++ binding or a
    Python mock) must provide these methods.
    """

    @abstractmethod
    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        alpha: float,
        nlambda: int,
        # ... other core glmnet parameters will be added here
    ) -> Dict[str, Any]:
        """
        Calls the core glmnet solver to fit a model.

        This method is responsible for taking Python/NumPy data, passing it
        to the underlying computational engine (real or mocked), and returning
        the results in a structured format.

        Args:
            x (np.ndarray): The training data matrix of shape (n_samples, n_features).
            y (np.ndarray): The target vector of shape (n_samples,).
            alpha (float): The elastic net mixing parameter.
            nlambda (int): The number of lambda values in the regularization path.

        Returns:
            A dictionary containing the results from the solver. The essential keys are:
                - 'a0': The intercept vector for each lambda value.
                - 'ca': The coefficient matrix for each lambda value.
                - 'n_passes': The number of passes the solver took.
                - 'jerr': An error code from the Fortran/C++ backend (0 for success).
        """
        pass