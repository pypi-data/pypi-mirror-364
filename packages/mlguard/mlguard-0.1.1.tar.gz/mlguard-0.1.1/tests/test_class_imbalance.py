import numpy as np
from mlguard.class_imbalance import ClassImbalanceChecker

def test_balanced_class_distribution():
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1])  # balanced
    result = ClassImbalanceChecker.check_class_distribution(y, plot=False)

    assert isinstance(result, dict)
    assert 'imbalance_status' in result
    assert result['imbalance_status'] == 'Balanced Distribution'
    assert result['imbalance_ratio'] <= 0.2  # Should not exceed default thrsehold


def test_imbalanced_class_distribution():
    y = np.array([0, 0, 0, 0, 0, 1, 0, 0])  # imbalanced
    result = ClassImbalanceChecker.check_class_distribution(y, imbalance_threshold=0.1, plot=False)

    assert isinstance(result, dict)
    assert 'imbalance_status' in result
    assert result['imbalance_status'] == 'Class Imbalance Detected'
    assert result['imbalance_ratio'] > 0.1


def test_invalid_target_type():
    try:
        y = np.random.randn(10)  # non classification 
        ClassImbalanceChecker.check_class_distribution(y, plot=False)
    except Exception as e:
        assert isinstance(e, TypeError) or isinstance(e, ValueError)


test_invalid_target_type()