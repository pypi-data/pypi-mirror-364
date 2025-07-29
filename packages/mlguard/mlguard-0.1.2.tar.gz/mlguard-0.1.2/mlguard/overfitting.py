import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from mlguard.utils import get_model_type, validate_target_type, validate_model_capability, is_higher_better
from sklearn.utils.validation import check_is_fitted


class OverfittingChecker:
    """
    Detects overfitting or underfitting in scikit-learn models using learning curve analysis.
    """

    @staticmethod
    def check_learning_curve(model, X, y, cv=5, scoring=None, train_sizes=np.linspace(0.1, 1.0, 5), plot=True,high_train_thresh=0.9, low_test_thresh=0.7, gap_thresh=0.2):
        """
        Runs learning curve analysis and reports fit status.

        Parameters:
            model (sklearn.base.BaseEstimator): A scikit-learn model.
            X (array-like): Feature matrix.
            y (array-like): Target vector.
            cv (int): Number of cross-validation folds.
            scoring (str or None): Scoring metric like 'accuracy' or 'r2'. If None, auto-selected.
            train_sizes (array): Training sizes to use.
            plot (bool): Whether to plot learning curve.
            high_train_thresh (float): Threshold for high training score.
            low_test_thresh (float): Threshold for low test score.
            gap_thresh (float): Threshold for train-test performance gap.

        Returns:
            dict: Summary of fit status and scores.
        """

        # checks whether its sclearn model or not 
        validate_model_capability(model, ['fit', 'predict'])


        try:
            check_is_fitted(model)
        except Exception as e:
            raise ValueError(f"model is not fitted yet. please fit the model before passing to this checker. original error: {str(e)}")


        # model type detection
        model_type = get_model_type(model)

        # target validation
        if model_type == 'classifier':
            validate_target_type(y, 'classification')
            default_scoring = 'accuracy'
        elif model_type == 'regressor':
            validate_target_type(y, 'regression')
            default_scoring = 'r2'
        else:
            raise TypeError(f"Unsupported model type: {model_type}. Only classifiers and regressors allowed.")

        #  auto selection  scoring if not provided
        if scoring is None:
            scoring = default_scoring

        # learning curve test below 
        train_sizes, train_scores, test_scores = learning_curve(model, X, y, cv=cv, scoring=scoring, train_sizes=train_sizes, n_jobs=-1)

        # mean scores
        train_mean = np.mean(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        train_final = train_mean[-1]
        test_final = test_mean[-1]
        gap = train_final - test_final

        higher_is_better = is_higher_better(scoring)

        if higher_is_better:
            good_train = train_final > high_train_thresh
            poor_test = test_final < low_test_thresh
            large_gap = gap > gap_thresh
        else:
            good_train = train_final < high_train_thresh
            poor_test = test_final > low_test_thresh
            large_gap = abs(gap) > gap_thresh

        if good_train and poor_test and large_gap:
            status = "Overfitting Detected"
        elif not good_train and poor_test:
            status = "Underfitting Detected"
        else:
            status = "Good Fit"

        #  plotting 
        if plot:
            plt.figure(figsize=(8, 6))
            plt.plot(train_sizes, train_mean, 'o-', color="r", label="Training Score")
            plt.plot(train_sizes, test_mean, 'o-', color="g", label="Cross-Validation Score")
            plt.xlabel("Training Set Size")
            plt.ylabel(scoring.capitalize())
            plt.title(f"Learning Curve - Status: {status}")
            plt.legend(loc="best")
            plt.grid()
            plt.tight_layout()
            plt.show()

        
        return {
            "train_sizes": train_sizes.tolist(),
            "train_scores_mean": train_mean.tolist(),
            "test_scores_mean": test_mean.tolist(),
            "final_train_score": float(train_final),
            "final_test_score": float(test_final),
            "train_test_gap": float(gap),
            "fit_status": status,
            "scoring_metric": scoring
        }



  