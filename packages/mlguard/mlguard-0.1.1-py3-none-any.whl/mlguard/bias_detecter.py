import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from mlguard.utils import get_model_type, validate_target_type, validate_model_capability
from sklearn.utils.validation import check_is_fitted

class BiasDetectionChecker:
    """
    Detects performance bias across groups within a sensitive feature (like gender, age)
    """

    @staticmethod
    def check_group_bias(model, X, y, sensitive_feature, metric='accuracy', threshold=0.1):
        """
        Checks if model performance differs significantly across groups of a sensitive feature.

        Parameters:
            model (sklearn.base.BaseEstimator): Trained sklearn model.
            X (DataFrame or ndarray): Features (must include sensitive feature if DataFrame).
            y (array-like): True target labels.
            sensitive_feature (str or int): Feature name (if DataFrame) or column index (if ndarray).
            metric (str): Metric to evaluate (currently supports 'accuracy').
            threshold (float): Allowed max difference in group performance.

        Returns:
            dict: Group-wise performance, bias gap, and bias status.
        """

        # validate model capability and fitted status
        validate_model_capability(model, ['predict'])
        check_is_fitted(model)

        # target type validation (only classification supported for hamna)
        model_type = get_model_type(model)
        if model_type != 'classifier':
            raise TypeError("Bias detection currently supports only classification models.")

        validate_target_type(y, 'classification')

        # extract imoprtant feature values
        if isinstance(X, pd.DataFrame):
            if sensitive_feature not in X.columns:
                raise ValueError(f"Sensitive feature '{sensitive_feature}' not found in DataFrame columns.")
            sensitive_values = X[sensitive_feature].values
            X_wo_sensitive = X.drop(columns=[sensitive_feature])
        else:
            sensitive_values = X[:, sensitive_feature]
            X_wo_sensitive = np.delete(X, sensitive_feature, axis=1)

        unique_groups = np.unique(sensitive_values)
        group_performance = {}

        # evaluate model accuracy for each group
        y_pred = model.predict(X_wo_sensitive)

        for group in unique_groups:
            group_mask = sensitive_values == group
            if np.sum(group_mask) == 0:
                continue  # Skip if no samples for the group

            group_y_true = y[group_mask]
            group_y_pred = y_pred[group_mask]

            if metric == 'accuracy':
                score = accuracy_score(group_y_true, group_y_pred)
            else:
                raise ValueError(f"Unsupported metric '{metric}'")

            group_performance[group] = score

        # bias gap calculation
        scores = np.array(list(group_performance.values()))
        max_score = np.max(scores)
        min_score = np.min(scores)
        bias_gap = max_score - min_score

        if bias_gap > threshold:
            status = "Bias Detected"
        else:
            status = "No Significant Bias"


        return {
            "group_performance": group_performance,
            "bias_gap": float(bias_gap),
            "bias_threshold": threshold,
            "bias_status": status,
            "metric_used": metric
        }