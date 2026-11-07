# Split Conformal Prediction Report: MobiURL-Guard (Research Gap 3)

## 1. Conformal Theoretical Framework
- **Guarantee:** Finite-sample marginal coverage under the exchangeability assumption.
- **Quantile Correction:** Finite-sample non-conformity threshold computed strictly on the dedicated calibration partition (N_cal = 1500).
- **Set Outcomes:**
  1. `{Legitimate}` (High-confidence benign)
  2. `{Malicious}` (High-confidence malicious)
  3. `{Legitimate, Malicious}` (Uncertain / Insufficient evidence)

---

## 2. Empirical Coverage Across Nominal Targets

| Target Nominal Coverage | Selected $\alpha$ | Non-Conformity Threshold $\hat{q}$ | Empirical Test Coverage | Average Set Size | Singleton Rate | Uncertainty Rate | Coverage Guarantee Met |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **90%** | 0.10 | 0.2262 | **90.47%** | 0.913 | 91.27% | 0.00% | PASSED |
| **95%** | 0.05 | 0.3169 | **96.20%** | 0.975 | 97.47% | 0.00% | PASSED |
| **99%** | 0.01 | 0.8242 | **99.87%** | 1.111 | 88.93% | 11.07% | PASSED |

---

## 3. Class-Conditioned Coverage (95% Nominal)

- **Benign Class Coverage:** `96.20%`
- **Malicious Class Coverage:** `0.00%`

---

## 4. Mobile Fail-Safe Handling
When the prediction set yields `{Legitimate, Malicious}`, MobiURL-Guard returns:
> *"Unable to determine this URL reliably. Exercise caution."*
This prevents deceptive false certainty on borderline or ambiguous mobile inputs.
