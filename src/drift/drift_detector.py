"""
Concept Drift and Distribution Shift Monitoring for MobiURL-Guard (Research Gap 11).
Monitors incoming URL feature distributions using:
1. Population Stability Index (PSI)
2. Feature-wise drift breakdown
3. Retraining trigger and reporting protocol
"""

import math
from typing import Dict, List, Any, Tuple


def calculate_psi(baseline: List[float], target: List[float], num_bins: int = 10) -> float:
    """
    Calculate Population Stability Index (PSI) between baseline and incoming feature distributions.
    PSI = sum((target_pct - baseline_pct) * ln(target_pct / baseline_pct))
    """
    if not baseline or not target:
        return 0.0

    all_vals = baseline + target
    min_v = min(all_vals)
    max_v = max(all_vals)
    if min_v == max_v:
        return 0.0

    step = (max_v - min_v) / num_bins
    eps = 1e-4

    n_base = len(baseline)
    n_target = len(target)
    psi = 0.0

    for i in range(num_bins):
        low = min_v + i * step
        high = min_v + (i + 1) * step if i < (num_bins - 1) else max_v + 1e-5

        b_count = sum(1 for v in baseline if low <= v < high)
        t_count = sum(1 for v in target if low <= v < high)

        b_pct = max(eps, b_count / n_base)
        t_pct = max(eps, t_count / n_target)

        psi += (t_pct - b_pct) * math.log(t_pct / b_pct)

    return round(psi, 4)


class DriftDetector:
    """
    Detects covariate shift and concept drift between reference and production streams.
    """

    def __init__(self, psi_threshold: float = 0.25):
        self.psi_threshold = psi_threshold
        self.baseline_distributions: Dict[str, List[float]] = {}

    def fit_baseline(self, feature_dicts: List[Dict[str, float]]):
        """Register baseline feature distribution from verified training set."""
        if not feature_dicts:
            return
        keys = list(feature_dicts[0].keys())
        for k in keys:
            self.baseline_distributions[k] = [d.get(k, 0.0) for d in feature_dicts]

    def evaluate_batch(self, incoming_dicts: List[Dict[str, float]]) -> Dict[str, Any]:
        """Evaluate a batch of incoming URLs for distribution drift."""
        if not self.baseline_distributions:
            return {"drift_detected": False, "status": "No baseline registered"}

        feature_psi = {}
        drifted_features = []

        for fname, base_vals in self.baseline_distributions.items():
            curr_vals = [d.get(fname, 0.0) for d in incoming_dicts]
            psi_val = calculate_psi(base_vals, curr_vals)
            feature_psi[fname] = psi_val
            if psi_val >= self.psi_threshold:
                drifted_features.append({"feature": fname, "psi": psi_val})

        overall_drift = len(drifted_features) >= 2 or any(f["psi"] > 0.40 for f in drifted_features)

        return {
            "drift_detected": overall_drift,
            "drift_severity": "High (Retraining Recommended)" if overall_drift else ("Moderate" if drifted_features else "Stable"),
            "drifted_features_count": len(drifted_features),
            "drifted_features": drifted_features,
            "feature_psi_scores": feature_psi,
            "action": "Trigger controlled offline model update" if overall_drift else "Continue monitoring"
        }
