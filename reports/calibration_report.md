# Probability Calibration Report: MobiURL-Guard (Research Gap 2)

## 1. Methodology
- **Calibration Protocol:** Separate holdout partition (10% of dataset, N=1500), independent of test set.
- **Method:** Platt Scaling (Sigmoid logistic calibration on model log-odds).
- **Evaluation Set:** Independent Test Set (N=1500).

---

## 2. Quantitative Calibration Improvements

| Metric | Uncalibrated Model | Calibrated Model (Platt) | Improvement |
| :--- | :--- | :--- | :--- |
| **Expected Calibration Error (ECE)** | **0.0942** | **0.0690** | **26.8% reduction** |
| **Maximum Calibration Error (MCE)** | 0.9500 | 0.9685 | -1.9% reduction |
| **Brier Score** | 0.0389 | 0.0201 | 48.3% improvement |

---

## 3. Reliability Diagram Bin Breakdown (Calibrated)

| Bin Range | Sample Count | Mean Confidence | Observed Accuracy | Calibration Gap |
| :--- | :--- | :--- | :--- | :--- |
| 0.00 - 0.10 | 1196 | 0.0221 | 0.0000 | 0.0221 |
| 0.10 - 0.20 | 148 | 0.1367 | 0.0000 | 0.1367 |
| 0.20 - 0.30 | 92 | 0.2486 | 0.0000 | 0.2486 |
| 0.30 - 0.40 | 24 | 0.3420 | 0.0000 | 0.3420 |
| 0.40 - 0.50 | 15 | 0.4799 | 0.0000 | 0.4799 |
| 0.50 - 0.60 | 3 | 0.5532 | 0.0000 | 0.5532 |
| 0.60 - 0.70 | 3 | 0.6388 | 0.0000 | 0.6388 |
| 0.70 - 0.80 | 8 | 0.7215 | 0.0000 | 0.7215 |
| 0.80 - 0.90 | 10 | 0.8289 | 0.0000 | 0.8289 |
| 0.90 - 1.00 | 1 | 0.9685 | 0.0000 | 0.9685 |
