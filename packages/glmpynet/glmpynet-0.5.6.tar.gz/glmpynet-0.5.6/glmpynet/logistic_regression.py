"""
This module contains the LogisticRegression class, a scikit-learn compatible wrapper
for penalized logistic regression.
"""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
from sklearn.utils._param_validation import InvalidParameterError
from sklearn.utils.multiclass import unique_labels, type_of_target
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted, validate_data

# Import our new binding interface and mock implementation
from .binding.base import GlmNetBinding
from .binding.mock import MockGlmNetBinding


class LogisticRegression(ClassifierMixin, BaseEstimator):
    """
    A scikit-learn compatible estimator for penalized logistic regression.

    This class provides a user-friendly hybrid API. By default, it accepts
    scikit-learn style parameters like `C` and `penalty`. It also provides an
    "escape hatch" for advanced users to pass glmnet-native parameters like
    `alpha` and `nlambda` directly.

    Parameters
    ----------
    penalty : {'l1', 'l2'}, default='l2'
        Specifies the norm of the penalty.
    C : float, default=1.0
        Inverse of regularization strength; must be a positive float.
    alpha : float, optional
        The elastic net mixing parameter, with 0 <= alpha <= 1. If provided,
        this will override the `penalty` parameter.
    nlambda : int, default=100
        The number of lambda values in the regularization path.
    """

    def __init__(self, penalty: str = 'l2', C: float = 1.0, alpha: float = None, nlambda: int = 100,
                 binding: GlmNetBinding = None):
        """
        Initializes the LogisticRegression model. The constructor is "lean"
        and only stores parameters. All validation and translation happens in `fit`.
        """
        self.penalty = penalty
        self.C = C
        self.alpha = alpha
        self.nlambda = nlambda
        self.binding = binding

    def _validate_and_translate_params(self):
        """
        Validates hyperparameters and translates sklearn-style params to glmnet-style.
        This is called at the beginning of fit().
        """
        if self.C <= 0:
            raise InvalidParameterError(
                f"The 'C' parameter of LogisticRegression must be a positive float. "
                f"Got {self.C} instead."
            )

        # Determine the final alpha value
        if self.alpha is not None:
            # User provided alpha directly, it takes precedence
            if not 0 <= self.alpha <= 1:
                raise InvalidParameterError(f"alpha must be in [0, 1]; got (alpha={self.alpha})")
            final_alpha = self.alpha
        else:
            # Translate from penalty
            if self.penalty == 'l1':
                final_alpha = 1.0
            elif self.penalty == 'l2':
                final_alpha = 0.0
            else:
                # --- THIS IS THE FIX ---
                # Raise the specific error type that the scikit-learn ecosystem expects.
                raise InvalidParameterError(
                    f"The 'penalty' parameter of LogisticRegression must be 'l1' or 'l2'. "
                    f"Got '{self.penalty}' instead."
                )

        return {"alpha": final_alpha, "nlambda": self.nlambda}

    def fit(self, X, y):
        """
        Fit the logistic regression model according to the given training data.
        """
        # Step 1: Validate and translate hyperparameters
        glmnet_params = self._validate_and_translate_params()

        # Step 2: Validate input data
        X, y = check_X_y(X, y, accept_sparse=True)
        self.classes_ = unique_labels(y)
        self.n_features_in_ = X.shape[1]

        # Use the recommended scikit-learn utility to check the target type.
        # This ensures we raise the exact error message that check_estimator expects.
        y_type = type_of_target(y)
        if y_type != "binary":
            raise ValueError(
                "Only binary classification is supported. The type of the target "
                f"is {y_type}."
            )

        # Step 3: Instantiate the binding
        if self.binding is None:
            self.binding_ = MockGlmNetBinding()
        else:
            self.binding_ = self.binding

        # Step 4: Call the binding's fit method with the translated parameters
        results = self.binding_.fit(
            x=X,
            y=y,
            alpha=glmnet_params['alpha'],
            nlambda=glmnet_params['nlambda']
        )

        # Step 5: Store the fitted coefficients
        lambda_idx_to_use = self.nlambda // 2
        self.intercept_ = np.array([results['a0'][lambda_idx_to_use]])
        self.coef_ = results['ca'][:, lambda_idx_to_use].T.reshape(1, -1)

        return self

    def _decision_function(self, X):
        """Calculate the linear decision function."""
        check_is_fitted(self)
        # Use validate_data to ensure n_features_in_ is checked correctly
        X = validate_data(self, X, accept_sparse=True, reset=False)
        return (X @ self.coef_.T) + self.intercept_

    def predict(self, X):
        """
        Predict class labels for samples in X.
        """
        scores = self._decision_function(X).ravel()
        predictions = (scores > 0).astype(int)
        return self.classes_[predictions]

    def predict_proba(self, X):
        """
        Probability estimates for samples in X.
        """
        scores = self._decision_function(X).ravel()
        prob_class_1 = 1 / (1 + np.exp(-scores))
        prob_class_0 = 1 - prob_class_1
        return np.vstack((prob_class_0, prob_class_1)).T

    def _more_tags(self):
        """
        Provides custom metadata to scikit-learn's tag system. This is the
        correct and documented way to override a default tag. BaseEstimator's
        __sklearn_tags__ method will find and use this.
        """
        return {"binary_only": True}

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.classifier_tags.multi_class = False
        tags.classifier_tags.multi_label = False
        tags.classifier_tags.poor_score = True
        tags.estimator_type = 'classifier'
        tags.input_tags.sparse = True
        return tags
