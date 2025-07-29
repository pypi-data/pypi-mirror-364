from sklearn.base import ClassifierMixin, RegressorMixin, ClusterMixin
from sklearn.utils.multiclass import type_of_target

def get_model_type(model):
    if isinstance(model, ClassifierMixin):
        return 'classifier'
    elif isinstance(model, RegressorMixin):
        return 'regressor'
    elif isinstance(model, ClusterMixin):
        return 'cluster'
    else:
        return 'unknown'
    


def validate_target_type(y, expected_type):
    target_type = type_of_target(y)

    if expected_type == 'classification' and target_type not in ['binary', 'multiclass', 'multilabel-indicator']:
        raise TypeError(f"Expected classification target (binary/multiclass), but got '{target_type}'.")
    
    if expected_type == 'regression' and target_type not in ['continuous', 'continuous-multioutput']:
        raise TypeError(f"Expected regression target (continuous), but got '{target_type}'.")




def validate_model_capability(model, required_methods):
    for method in required_methods:
        if not hasattr(model, method):
            raise TypeError(f"The model does not have required method: '{method}'")



def is_higher_better(scoring):
    """
    Determines if a scoring metric is higher is better or lower is better
    """
    lower_better_metrics = [
        'neg_mean_squared_error', 
        'neg_root_mean_squared_error', 
        'neg_mean_absolute_error', 
        'neg_log_loss'
    ]

    if scoring is None:
        return True  # Default assumption for accuracy/r2

    if scoring in lower_better_metrics or scoring.startswith('neg_'):
        return False
    else:
        return True


