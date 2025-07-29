import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.utils.multiclass import type_of_target
from mlguard.utils import get_model_type, validate_target_type, validate_model_capability

class ClassImbalanceChecker:
    """
    Checks for class imbalance in classification datasets.
    """

    @staticmethod
    def check_class_distribution(y, imbalance_threshold=0.2, plot=True):
        """
        Analyze class distribution for imbalance.

        Parameters:
            y (array-like): Target vector (classification labels)
            imbalance_threshold (float): Allowed max ratio difference between classes (default 0.2 → 20%)
            plot (bool): Whether to visualize class distribution

        Returns:
            dict: Summary with class counts, imbalance ratio, and imbalance status
        """

        # validate target type is classification
        validate_target_type(y, 'classification')

        # cuont samples per class
        class_counts = Counter(y)
        total_samples = len(y)
        class_frequencies = {cls: count / total_samples for cls, count in class_counts.items()}

        # calculate imbalance ratio (max freq - min freq)
        frequencies = np.array(list(class_frequencies.values()))
        max_freq = np.max(frequencies)
        min_freq = np.min(frequencies)
        imbalance_ratio = max_freq - min_freq

        
        if imbalance_ratio > imbalance_threshold:
            status = "Class Imbalance Detected"
        else:
            status = "Balanced Distribution"

        # ploting 
        if plot:
            plt.figure(figsize=(6, 4))
            plt.bar(class_counts.keys(), class_counts.values(), color='skyblue')
            plt.xlabel("Class Labels")
            plt.ylabel("Sample Count")
            plt.title(f"Class Distribution - Status: {status}")
            plt.tight_layout()
            plt.show()

        
        return {
            "class_counts": dict(class_counts),
            "class_frequencies": class_frequencies,
            "imbalance_ratio": float(imbalance_ratio),
            "imbalance_threshold": imbalance_threshold,
            "imbalance_status": status
        }

