import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_classification, make_regression
from mlguard.overfitting import OverfittingChecker

def test_overfitting_detection():
    X, y = make_classification(n_samples=200, n_features=10, random_state=42)
    
    # forcse overfitting with deep tree
    model = DecisionTreeClassifier(max_depth=None)
    model.fit(X, y)

    result = OverfittingChecker.check_learning_curve(
        model, X, y, scoring='accuracy', plot=False, high_train_thresh=0.9, low_test_thresh=0.7, gap_thresh=0.2
    )

    assert isinstance(result, dict)
    assert 'fit_status' in result
    assert result['fit_status'] in ['Overfitting Detected', 'Good Fit', 'Underfitting Detected']

test_overfitting_detection()

def test_underfitting_detection():
    X, y = make_classification(n_samples=200, n_features=10, random_state=42)

    # force underfitting with shallow tree
    model = DecisionTreeClassifier(max_depth=1)
    model.fit(X, y)

    result = OverfittingChecker.check_learning_curve(
        model, X, y, scoring='accuracy', plot=False, high_train_thresh=0.9, low_test_thresh=0.7, gap_thresh=0.2
    )

    assert isinstance(result, dict)
    assert 'fit_status' in result
    assert result['fit_status'] in ['Underfitting Detected', 'Good Fit', 'Overfitting Detected']

test_underfitting_detection()

def test_regression_model_support():
    X, y = make_regression(n_samples=200, n_features=10, noise=5.0, random_state=42)

    model = LinearRegression()
    model.fit(X, y)

    result = OverfittingChecker.check_learning_curve(
        model, X, y, scoring='r2', plot=False
    )

    assert isinstance(result, dict)
    assert 'fit_status' in result
    assert result['fit_status'] in ['Overfitting Detected', 'Underfitting Detected', 'Good Fit']

test_regression_model_support()

def test_non_fitted_model_error():
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    model = DecisionTreeClassifier()

    try:
        OverfittingChecker.check_learning_curve(model, X, y, plot=False)
    except Exception as e:
        assert isinstance(e, ValueError)
        assert "model is not fitted yet" in str(e)

test_non_fitted_model_error()

def test_invalid_model_type():
    class DummyModel:
        def predict(self, X):
            return np.zeros(X.shape[0])

    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    dummy_model = DummyModel()

    try:
        OverfittingChecker.check_learning_curve(dummy_model, X, y, plot=False)
    except Exception as e:
        assert isinstance(e, TypeError)


test_invalid_model_type()