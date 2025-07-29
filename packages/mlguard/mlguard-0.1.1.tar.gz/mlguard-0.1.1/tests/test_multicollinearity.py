import pandas as pd
from mlguard.multicollinearitychecker import MulticollinearityChecker
import numpy as np 

def test_high_multicollinearity_detection():
    #  two collinear features
    X = pd.DataFrame({
        'f1': [1, 2, 3, 4, 5],
        'f2': [2, 4, 6, 8, 10],  # Perfect linear relation with f1
        'f3': [5, 3, 6, 2, 1]   
    })

    result = MulticollinearityChecker.check_vif(X, vif_threshold=5.0)

    assert isinstance(result, dict)
    assert 'vif_scores' in result
    assert 'high_vif_features' in result
    assert 'collinearity_status' in result
    assert result['collinearity_status'] == "High Multicollinearity Detected"
    assert any(v > 5.0 for v in result['vif_scores'].values())



test_high_multicollinearity_detection()

def test_no_multicollinearity_detection():
    np.random.seed(42)
    # Random independent features (uncorrelated)
    X = pd.DataFrame({
        "A": np.random.rand(100),
        "B": np.random.rand(100),
        "C": np.random.rand(100)
    })

    result = MulticollinearityChecker.check_vif(X)

    print("VIF TEST RESULT:", result)

    assert isinstance(result, dict)
    assert result['collinearity_status'] == "No Significant Multicollinearity"
    assert all(vif < 5 for vif in result['vif_scores'].values())

test_no_multicollinearity_detection()

def test_invalid_input_type():
    # a non dataFrame, non ndarray input
    try:
        MulticollinearityChecker.check_vif([1, 2, 3, 4])
    except Exception as e:
        assert isinstance(e, TypeError)


test_invalid_input_type()

def test_too_few_features():
    # less than 2 data
    X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
    try:
        MulticollinearityChecker.check_vif(X)
    except Exception as e:
        assert isinstance(e, ValueError)


test_too_few_features()