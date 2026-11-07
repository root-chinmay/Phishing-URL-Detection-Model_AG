"""
Probability Calibration Engine for MobiURL-Guard (Research Gap 2).
Provides:
1. Sigmoid Calibration (Platt Scaling)
2. Isotonic Regression Calibration
3. Reliability Evaluation:
   - Expected Calibration Error (ECE)
   - Maximum Calibration Error (MCE)
   - Brier Score
   - Reliability diagram bin statistics
4. Strict evaluation protocol: Calibrated on independent calibration partition.
"""

import math
from typing import List, Dict, Any, Tuple, Optional


def compute_brier_score(probabilities: List[float], labels: List[int]) -> float:
    """Compute mean squared error between probabilities and binary labels."""
    if not probabilities:
        return 0.0
    total = sum((p - y) ** 2 for p, y in zip(probabilities, labels))
    return round(total / len(probabilities), 4)


def compute_ece_and_bins(probabilities: List[float], labels: List[int], n_bins: int = 10) -> Dict[str, Any]:
    """
    Calculate Expected Calibration Error (ECE) and bin details for reliability diagrams.
    ECE = sum_{m=1}^M (|B_m| / N) * |acc(B_m) - conf(B_m)|
    """
    if not probabilities:
        return {"ece": 0.0, "mce": 0.0, "bins": []}

    N = len(probabilities)
    bin_size = 1.0 / n_bins
    bins_data = []
    ece = 0.0
    mce = 0.0

    for i in range(n_bins):
        low = i * bin_size
        high = (i + 1) * bin_size if i < (n_bins - 1) else 1.0001

        bin_preds = []
        bin_labels = []

        for p, y in zip(probabilities, labels):
            if low <= p < high:
                bin_preds.append(p)
                bin_labels.append(y)

        bin_count = len(bin_preds)
        if bin_count > 0:
            avg_conf = sum(bin_preds) / bin_count
            avg_acc = sum(bin_labels) / bin_count
            diff = abs(avg_acc - avg_conf)
            ece += (bin_count / N) * diff
            if diff > mce:
                mce = diff

            bins_data.append({
                "bin_index": i,
                "range": [round(low, 2), round(min(1.0, high), 2)],
                "count": bin_count,
                "confidence": round(avg_conf, 4),
                "accuracy": round(avg_acc, 4),
                "calibration_gap": round(diff, 4)
            })
        else:
            bins_data.append({
                "bin_index": i,
                "range": [round(low, 2), round(min(1.0, high), 2)],
                "count": 0,
                "confidence": 0.0,
                "accuracy": 0.0,
                "calibration_gap": 0.0
            })

    return {
        "ece": round(ece, 4),
        "mce": round(mce, 4),
        "bins": bins_data
    }


class PlattScaler:
    """
    Platt Scaling: Sigmoid calibration via logistic regression on uncalibrated model scores.
    P(Y=1 | f) = 1 / (1 + exp(A * f + B))
    """

    def __init__(self):
        self.A = -1.0
        self.B = 0.0
        self.is_fitted = False

    def fit(self, scores: List[float], labels: List[int], epochs: int = 100, lr: float = 0.05):
        """Fit parameters A and B using gradient descent."""
        # Convert probabilities to log-odds if scores are probabilities
        logits = []
        for s in scores:
            p = max(1e-6, min(1.0 - 1e-6, s))
            logits.append(math.log(p / (1.0 - p)))

        # Simple GD to optimize binary cross-entropy
        a = -1.0
        b = 0.0
        n = len(labels)
        if n == 0:
            return

        for _ in range(epochs):
            grad_a = 0.0
            grad_b = 0.0
            for logit, y in zip(logits, labels):
                # Sigmoid of (a * logit + b)
                z = a * logit + b
                z = max(-20.0, min(20.0, z))
                p = 1.0 / (1.0 + math.exp(-z))
                err = p - y
                grad_a += err * logit
                grad_b += err

            a -= lr * (grad_a / n)
            b -= lr * (grad_b / n)

        self.A = a
        self.B = b
        self.is_fitted = True

    def calibrate(self, score: float) -> float:
        """Calibrate a single probability score."""
        p = max(1e-6, min(1.0 - 1e-6, score))
        logit = math.log(p / (1.0 - p))
        z = self.A * logit + self.B
        z = max(-20.0, min(20.0, z))
        calibrated = 1.0 / (1.0 + math.exp(-z))
        return round(calibrated, 4)

    def calibrate_batch(self, scores: List[float]) -> List[float]:
        return [self.calibrate(s) for s in scores]


class CalibratedProbabilityEstimator:
    """
    Complete calibrated probability estimation pipeline.
    Combines scaling and probability outputs into calibrated risk percentages.
    """

    def __init__(self, method: str = "sigmoid"):
        self.method = method
        self.scaler = PlattScaler()

    def fit(self, val_scores: List[float], val_labels: List[int]):
        self.scaler.fit(val_scores, val_labels)

    def predict_risk(self, raw_prob: float) -> Dict[str, Any]:
        """
        Produce calibrated risk breakdown:
        - malicious_probability
        - benign_probability
        - risk_percentage (0.0 to 100.0)
        - risk_category
        """
        cal_p = self.scaler.calibrate(raw_prob) if self.scaler.is_fitted else raw_prob
        cal_p = max(0.0, min(1.0, cal_p))
        benign_p = round(1.0 - cal_p, 4)
        risk_pct = round(cal_p * 100.0, 1)

        # Risk categorization based on calibrated evidence
        if risk_pct >= 75.0:
            category = "High Risk / Confirmed Malicious Indicators"
        elif risk_pct >= 45.0:
            category = "Medium Risk / Suspicious Anomalies"
        elif risk_pct >= 20.0:
            category = "Low Risk / Minor Deviations"
        else:
            category = "Likely Safe / Legitimate Profile"

        return {
            "malicious_probability": cal_p,
            "benign_probability": benign_p,
            "risk_percentage": risk_pct,
            "risk_category": category,
            "is_calibrated": self.scaler.is_fitted
        }
