"""
Conformal Prediction Engine for MobiURL-Guard (Research Gap 3).
Implements Inductive (Split) Conformal Prediction for Binary Classification.
Produces mathematically valid prediction sets with guaranteed marginal coverage under exchangeability:
- {Legitimate}
- {Malicious}
- {Legitimate, Malicious} -> Uncertain / Insufficient Evidence

Implements finite-sample quantile correction:
q_val = ceil((n + 1) * (1 - alpha)) / n
"""

import math
from typing import List, Dict, Any, Tuple, Optional


class ConformalPredictor:
    """
    Split Conformal Classification with finite-sample quantile correction.
    """

    def __init__(self, alpha: float = 0.05):
        """
        alpha: Error rate (e.g., 0.05 corresponds to 95% nominal coverage).
        """
        self.alpha = alpha
        self.q_hat = 1.0
        self.is_calibrated = False
        self.calibration_size = 0

    def fit_calibration(self, probas_cal: List[float], labels_cal: List[int]):
        """
        Compute non-conformity quantile on a dedicated calibration partition.
        Non-conformity score: s_i = 1 - P(y_i | x_i)
        """
        n = len(labels_cal)
        if n == 0:
            raise ValueError("Calibration set cannot be empty.")

        scores = []
        for p_mal, y in zip(probas_cal, labels_cal):
            prob_true_class = p_mal if y == 1 else (1.0 - p_mal)
            score = 1.0 - prob_true_class
            scores.append(score)

        scores.sort()
        # Finite-sample quantile correction: index = ceil((n + 1) * (1 - alpha)) - 1
        rank = math.ceil((n + 1) * (1.0 - self.alpha)) - 1
        rank = min(max(0, rank), n - 1)
        self.q_hat = scores[rank]
        self.is_calibrated = True
        self.calibration_size = n
        return self.q_hat

    def predict_set(self, prob_malicious: float) -> Tuple[List[str], str]:
        """
        Generate conformal prediction set for a single URL probability.
        Includes class if: (1 - P(class | x)) <= q_hat
        which is equivalent to: P(class | x) >= 1 - q_hat
        """
        threshold = 1.0 - self.q_hat
        prob_benign = 1.0 - prob_malicious

        prediction_set = []
        if prob_benign >= threshold:
            prediction_set.append("Legitimate")
        if prob_malicious >= threshold:
            prediction_set.append("Malicious")

        # Determine uncertainty status
        if len(prediction_set) == 2:
            status = "Uncertain / Insufficient Evidence"
        elif len(prediction_set) == 1:
            status = f"Certain ({prediction_set[0]})"
        else:
            status = "Out of Nominal Distribution (Empty Set)"

        return prediction_set, status

    def evaluate_coverage(self, probas_test: List[float], labels_test: List[int]) -> Dict[str, Any]:
        """
        Empirically test conformal coverage, average set size, and singleton rate on test set.
        """
        if not self.is_calibrated:
            raise RuntimeError("ConformalPredictor must be calibrated on calibration data first.")

        covered_count = 0
        singleton_count = 0
        uncertain_count = 0
        empty_count = 0
        total_set_size = 0

        class_0_covered = 0
        class_0_total = 0
        class_1_covered = 0
        class_1_total = 0

        for p_mal, y in zip(probas_test, labels_test):
            true_label_str = "Malicious" if y == 1 else "Legitimate"
            pred_set, status = self.predict_set(p_mal)
            
            size = len(pred_set)
            total_set_size += size
            
            if true_label_str in pred_set:
                covered_count += 1
                if y == 1:
                    class_1_covered += 1
                else:
                    class_0_covered += 1

            if y == 1:
                class_1_total += 1
            else:
                class_0_total += 1

            if size == 1:
                singleton_count += 1
            elif size == 2:
                uncertain_count += 1
            elif size == 0:
                empty_count += 1

        n_test = len(labels_test)
        empirical_coverage = (covered_count / n_test) if n_test > 0 else 0.0
        avg_set_size = (total_set_size / n_test) if n_test > 0 else 0.0
        singleton_rate = (singleton_count / n_test) if n_test > 0 else 0.0
        uncertainty_rate = (uncertain_count / n_test) if n_test > 0 else 0.0

        cov_class_0 = (class_0_covered / class_0_total) if class_0_total > 0 else 0.0
        cov_class_1 = (class_1_covered / class_1_total) if class_1_total > 0 else 0.0

        return {
            "nominal_coverage": 1.0 - self.alpha,
            "alpha": self.alpha,
            "q_hat_cutoff": round(self.q_hat, 4),
            "calibration_samples": self.calibration_size,
            "test_samples": n_test,
            "empirical_coverage": round(empirical_coverage, 4),
            "average_set_size": round(avg_set_size, 4),
            "singleton_rate": round(singleton_rate, 4),
            "uncertainty_rate": round(uncertainty_rate, 4),
            "empty_rate": round(empty_count / n_test, 4) if n_test > 0 else 0.0,
            "class_0_benign_coverage": round(cov_class_0, 4),
            "class_1_malicious_coverage": round(cov_class_1, 4),
            "coverage_guarantee_met": empirical_coverage >= (1.0 - self.alpha - 0.02)
        }
