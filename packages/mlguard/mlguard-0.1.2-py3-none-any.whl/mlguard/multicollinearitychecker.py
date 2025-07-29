import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from mlguard.utils import validate_model_capability


class MulticollinearityChecker:
    """
     multicollinearity among numeric features using VIF
    """

    @staticmethod
    def check_vif(X, vif_threshold=5.0):
        """
        Calculates VIF for each feature and flags high multicollinearity.

        Parameters:
            X (DataFrame or ndarray): Feature matrix (must be numeric)
            vif_threshold (float): Threshold above which a feature is considered highly collinear (default=5.0)

        Returns:
            dict: VIF scores per feature, features above threshold, and overall status
        """

        if isinstance(X, pd.DataFrame):
            X_numeric = X.select_dtypes(include=[np.number])
            feature_names = X_numeric.columns.tolist()

        elif isinstance(X, np.ndarray):
            X_numeric = pd.DataFrame(X)
            feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        else:
            raise TypeError("X must be a pandas DataFrame or numpy ndarray.")

        if X_numeric.shape[1] < 2:
            raise ValueError("Multicollinearity check needs at least 2 numeric features.")

        # calculating VIFs
        vif_scores = []
        for i in range(X_numeric.shape[1]):
            vif = variance_inflation_factor(X_numeric.values, i)
            vif_scores.append(vif)

       
        vif_dict = dict(zip(feature_names, vif_scores))
        high_vif_features = [feature for feature, vif in vif_dict.items() if vif > vif_threshold]

        if len(high_vif_features) > 0:
            status = "High Multicollinearity Detected"
        else:
            status = "No Significant Multicollinearity"

        return {
            "vif_scores": vif_dict,
            "high_vif_features": high_vif_features,
            "vif_threshold": vif_threshold,
            "collinearity_status": status
        }

