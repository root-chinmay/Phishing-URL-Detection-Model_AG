"""
Out-of-Distribution (OOD) Detection Module for MobiURL-Guard.
Detects when incoming URL feature vectors deviate significantly from the training distribution.
Prevents false overconfidence on alien or zero-day URL formats.
"""

import math
from typing import Dict, List, Any, Optional


class OutOfDistributionDetector:
    """
    Evaluates Mahalanobis/Z-score distance against feature statistics of training set.
    """

    def __init__(self, z_threshold: float = 4.0):
        self.z_threshold = z_threshold
        self.feature_stats: Dict[str, Dict[str, float]] = {}
        self.is_fitted = False

    def fit(self, feature_dicts: List[Dict[str, float]]):
        """Fit feature means and standard deviations from training data."""
        if not feature_dicts:
            return

        feature_names = list(feature_dicts[0].keys())
        stats = {}
        n = len(feature_dicts)

        for fname in feature_names:
            vals = [d.get(fname, 0.0) for d in feature_dicts]
            mean = sum(vals) / n
            var = sum((v - mean) ** 2 for v in vals) / (n - 1) if n > 1 else 1e-4
            std = math.sqrt(max(1e-6, var))
            min_val = min(vals)
            max_val = max(vals)

            stats[fname] = {
                "mean": mean,
                "std": std,
                "min": min_val,
                "max": max_val
            }

        self.feature_stats = stats
        self.is_fitted = True

    def evaluate(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluate if a sample is OOD.
        Returns is_ood, max_z_score, and anomalous_features.
        """
        if not self.is_fitted:
            return {
                "is_out_of_distribution": False,
                "ood_score": 0.0,
                "anomalous_features": [],
                "status": "OOD detector not fitted"
            }

        anomalous = []
        max_z = 0.0
        z_sum = 0.0
        count = 0

        for fname, val in features.items():
            if fname in self.feature_stats:
                stat = self.feature_stats[fname]
                z = abs(val - stat["mean"]) / stat["std"]
                z_sum += z
                count += 1
                if z > max_z:
                    max_z = z
                if z > self.z_threshold:
                    anomalous.append({
                        "feature": fname,
                        "observed_value": round(val, 2),
                        "training_mean": round(stat["mean"], 2),
                        "z_score": round(z, 2)
                    })

        avg_z = (z_sum / count) if count > 0 else 0.0
        # Classified as OOD if multiple features severely deviate or average deviation is very high
        is_ood = (len(anomalous) >= 2) or (max_z >= 6.0) or (avg_z >= 2.5)

        return {
            "is_out_of_distribution": is_ood,
            "ood_score": round(max_z, 2),
            "average_z_deviation": round(avg_z, 2),
            "anomalous_features": anomalous[:4],
            "status": "Out of Distribution: Unfamiliar structural characteristics" if is_ood else "In-Distribution"
        }
