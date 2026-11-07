"""
Calibration and Conformal Prediction Pipeline for MobiURL-Guard.
Performs:
1. Probability calibration using separate calibration set (Platt Scaling & Isotonic)
2. Evaluation of Expected Calibration Error (ECE) and Brier Score
3. Split Conformal Prediction with finite-sample quantile correction
4. Generates reports/calibration_report.md and reports/conformal_report.md
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.loader import DatasetLoader
from src.data.validation import DataValidator
from src.data.splitting import DataSplitter
from src.data.preprocessing import DataPreprocessor
from src.distillation.student import CompactEnsembleStudent
from src.calibration.probability_calibration import (
    CalibratedProbabilityEstimator,
    compute_ece_and_bins,
    compute_brier_score
)
from src.uncertainty.conformal import ConformalPredictor


def run_calibration_and_conformal():
    print("[*] Starting Calibration and Conformal Prediction Pipeline...")
    model_path = os.path.join("models", "exported", "best_student_model.json")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Exported model not found at {model_path}. Run train_baselines.py first.")

    model = CompactEnsembleStudent.load_json(model_path)

    # Load dataset & partition
    loader = DatasetLoader()
    raw_records, _ = loader.load_raw_records()
    clean_records, _ = DataValidator.filter_clean_records(raw_records)
    splitter = DataSplitter(seed=42)
    deduped = splitter.deduplicate(clean_records)

    subset = deduped[:15000] if len(deduped) > 15000 else deduped
    train_recs, val_recs, cal_recs, test_recs = splitter.split_stratified(
        subset, train_ratio=0.70, val_ratio=0.10, cal_ratio=0.10, test_ratio=0.10
    )

    preprocessor = DataPreprocessor()
    X_cal, y_cal, _ = preprocessor.process_records(cal_recs)
    X_test, y_test, _ = preprocessor.process_records(test_recs)

    feat_names = preprocessor.feature_names

    # Compute raw model probabilities on calibration and test
    def get_probs(X):
        probs = []
        for row in X:
            f_dict = {fn: val for fn, val in zip(feat_names, row)}
            probs.append(model.predict_proba(f_dict))
        return probs

    raw_cal_probs = get_probs(X_cal)
    raw_test_probs = get_probs(X_test)

    # 1. Evaluate uncalibrated baseline metrics
    uncal_brier = compute_brier_score(raw_test_probs, y_test)
    uncal_ece_info = compute_ece_and_bins(raw_test_probs, y_test, n_bins=10)

    # 2. Fit Calibrator on independent calibration set
    calibrator = CalibratedProbabilityEstimator(method="sigmoid")
    calibrator.fit(raw_cal_probs, y_cal)

    cal_test_probs = [calibrator.predict_risk(p)["malicious_probability"] for p in raw_test_probs]
    cal_brier = compute_brier_score(cal_test_probs, y_test)
    cal_ece_info = compute_ece_and_bins(cal_test_probs, y_test, n_bins=10)

    print(f"[+] Calibration Results:")
    print(f"    - Uncalibrated ECE: {uncal_ece_info['ece']:.4f} | Brier: {uncal_brier:.4f}")
    print(f"    - Calibrated ECE:   {cal_ece_info['ece']:.4f} | Brier: {cal_brier:.4f}")

    # Generate calibration report
    cal_report_md = f"""# Probability Calibration Report: MobiURL-Guard (Research Gap 2)

## 1. Methodology
- **Calibration Protocol:** Separate holdout partition (10% of dataset, N={len(y_cal)}), independent of test set.
- **Method:** Platt Scaling (Sigmoid logistic calibration on model log-odds).
- **Evaluation Set:** Independent Test Set (N={len(y_test)}).

---

## 2. Quantitative Calibration Improvements

| Metric | Uncalibrated Model | Calibrated Model (Platt) | Improvement |
| :--- | :--- | :--- | :--- |
| **Expected Calibration Error (ECE)** | **{uncal_ece_info['ece']:.4f}** | **{cal_ece_info['ece']:.4f}** | **{((uncal_ece_info['ece'] - cal_ece_info['ece']) / max(1e-4, uncal_ece_info['ece']) * 100):.1f}% reduction** |
| **Maximum Calibration Error (MCE)** | {uncal_ece_info['mce']:.4f} | {cal_ece_info['mce']:.4f} | {((uncal_ece_info['mce'] - cal_ece_info['mce']) / max(1e-4, uncal_ece_info['mce']) * 100):.1f}% reduction |
| **Brier Score** | {uncal_brier:.4f} | {cal_brier:.4f} | {((uncal_brier - cal_brier) / max(1e-4, uncal_brier) * 100):.1f}% improvement |

---

## 3. Reliability Diagram Bin Breakdown (Calibrated)

| Bin Range | Sample Count | Mean Confidence | Observed Accuracy | Calibration Gap |
| :--- | :--- | :--- | :--- | :--- |
"""
    for b in cal_ece_info["bins"]:
        cal_report_md += f"| {b['range'][0]:.2f} - {b['range'][1]:.2f} | {b['count']} | {b['confidence']:.4f} | {b['accuracy']:.4f} | {b['calibration_gap']:.4f} |\n"

    cal_rep_path = os.path.join("reports", "calibration_report.md")
    with open(cal_rep_path, "w", encoding="utf-8") as f:
        f.write(cal_report_md)
    print(f"[+] Saved calibration report to: {cal_rep_path}")

    # 3. Conformal Prediction Evaluation at alpha in [0.10, 0.05, 0.01]
    print("[*] Evaluating Split Conformal Prediction...")
    conf_results = []
    alphas = [0.10, 0.05, 0.01]

    for alpha in alphas:
        cp = ConformalPredictor(alpha=alpha)
        cal_probs_cal = [calibrator.predict_risk(p)["malicious_probability"] for p in raw_cal_probs]
        cp.fit_calibration(cal_probs_cal, y_cal)
        eval_metrics = cp.evaluate_coverage(cal_test_probs, y_test)
        conf_results.append(eval_metrics)
        print(f"    - Alpha {alpha:.2f} (Nominal {eval_metrics['nominal_coverage']*100:.0f}%): Empirical Cov = {eval_metrics['empirical_coverage']*100:.2f}% | Set Size = {eval_metrics['average_set_size']:.3f} | Uncertainty = {eval_metrics['uncertainty_rate']*100:.2f}%")

    # Generate conformal report
    conf_report_md = f"""# Split Conformal Prediction Report: MobiURL-Guard (Research Gap 3)

## 1. Conformal Theoretical Framework
- **Guarantee:** Finite-sample marginal coverage under the exchangeability assumption.
- **Quantile Correction:** Finite-sample non-conformity threshold computed strictly on the dedicated calibration partition (N_cal = {len(y_cal)}).
- **Set Outcomes:**
  1. `{{Legitimate}}` (High-confidence benign)
  2. `{{Malicious}}` (High-confidence malicious)
  3. `{{Legitimate, Malicious}}` (Uncertain / Insufficient evidence)

---

## 2. Empirical Coverage Across Nominal Targets

| Target Nominal Coverage | Selected $\\alpha$ | Non-Conformity Threshold $\\hat{{q}}$ | Empirical Test Coverage | Average Set Size | Singleton Rate | Uncertainty Rate | Coverage Guarantee Met |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for res in conf_results:
        conf_report_md += f"| **{res['nominal_coverage']*100:.0f}%** | {res['alpha']:.2f} | {res['q_hat_cutoff']} | **{res['empirical_coverage']*100:.2f}%** | {res['average_set_size']:.3f} | {res['singleton_rate']*100:.2f}% | {res['uncertainty_rate']*100:.2f}% | {'PASSED' if res['coverage_guarantee_met'] else 'CHECK'} |\n"

    conf_report_md += f"""
---

## 3. Class-Conditioned Coverage (95% Nominal)

- **Benign Class Coverage:** `{conf_results[1]['class_0_benign_coverage']*100:.2f}%`
- **Malicious Class Coverage:** `{conf_results[1]['class_1_malicious_coverage']*100:.2f}%`

---

## 4. Mobile Fail-Safe Handling
When the prediction set yields `{{Legitimate, Malicious}}`, MobiURL-Guard returns:
> *"Unable to determine this URL reliably. Exercise caution."*
This prevents deceptive false certainty on borderline or ambiguous mobile inputs.
"""

    # Save calibration and conformal parameters manifest
    manifest_dir = os.path.join("models", "manifests")
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, "calibration_manifest.json")
    manifest_data = {
        "platt_scaler": {
            "A": calibrator.scaler.A,
            "B": calibrator.scaler.B,
            "is_fitted": calibrator.scaler.is_fitted
        },
        "conformal": {
            "alpha_0_10_q_hat": conf_results[0]["q_hat_cutoff"],
            "alpha_0_05_q_hat": conf_results[1]["q_hat_cutoff"],
            "alpha_0_01_q_hat": conf_results[2]["q_hat_cutoff"],
            "selected_q_hat": conf_results[1]["q_hat_cutoff"]
        },
        "calibration_samples": len(y_cal),
        "test_samples": len(y_test)
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[+] Saved calibration parameters manifest to: {manifest_path}")

    return conf_results


if __name__ == "__main__":
    run_calibration_and_conformal()
