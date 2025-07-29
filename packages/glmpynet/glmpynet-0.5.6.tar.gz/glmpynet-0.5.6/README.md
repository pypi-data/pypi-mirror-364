# glmpynet

[![CircleCI](https://circleci.com/gh/hrolfrc/glmpynet.svg?style=shield)](https://circleci.com/gh/hrolfrc/glmpynet)
[![ReadTheDocs](https://readthedocs.org/projects/glmpynet/badge/?version=latest)](https://glmpynet.readthedocs.io/en/latest/)
[![Codecov](https://codecov.io/gh/hrolfrc/glmpynet/branch/master/graph/badge.svg)](https://codecov.io/gh/hrolfrc/glmpynet)

## High-Performance Logistic Regression for Scikit-Learn

**glmpynet** is a Python package that provides a scikit-learn-compatible `LogisticRegression` API powered by the high-performance `glmnetpp` C++ library.

This project bridges the computational speed of `glmnetpp` with the ease-of-use of the Python data science ecosystem, acting as a drop-in replacement for `sklearn.linear_model.LogisticRegression` for regularized logistic regression.

## Key Features

* **High Performance**: Designed to leverage the optimized `glmnetpp` C++ backend for fitting models, suitable for large datasets. (Note: Currently uses a mock backend for API development).
* **Fully Scikit-learn Compatible**: Implements the full estimator API, including `fit`, `predict`, and `predict_proba`, enabling seamless integration with `sklearn` tools like `Pipeline` and `GridSearchCV`.
* **User-Friendly Hybrid API**: Accepts both standard Scikit-learn parameters (e.g., `C`, `penalty`) for ease of use and `glmnet`-native parameters (e.g., `alpha`, `nlambda`) for advanced control.
* **Robust Development**: Built with Bazel and Conda for reproducible builds, with a comprehensive test suite to ensure reliability.

## Installation

Once released, install `glmpynet` via pip:

```bash
pip install glmpynet
```

## Quick Start

Using `glmpynet` is as simple as any Scikit-learn estimator.

```python
from glmpynet.logistic_regression import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score

# 1. Generate synthetic data
X, y = make_classification(n_samples=1000, n_features=50, n_informative=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Instantiate and fit the model using familiar sklearn parameters
model = LogisticRegression(penalty='l1', C=0.5)
model.fit(X_train, y_train)

# 3. Make predictions
y_pred = model.predict(X_test)

# 4. Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")
```

## Project Status

The Python API for `glmpynet.LogisticRegression` is now **complete and fully tested** against a mock backend. The next major phase of development is to implement the real C++ binding that connects this API to the `glmnetpp` engine.

See the `ROADMAP.md` for the full development plan.

## Contributing

Contributions are welcome! See `CONTRIBUTING.md` for guidelines on reporting bugs, suggesting features, or submitting pull requests.

## License

This project is distributed under the GNU General Public License version 2.
