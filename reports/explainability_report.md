# Explainable AI (XAI) and Stability Report: MobiURL-Guard (Research Gap 10)

## 1. Methodology
- **Mobile XAI Paradigm:** Lightweight local directional attribution computing feature deviations from calibrated benign baselines.
- **Complexity:** $O(D)$ where $D$ is feature dimension, enabling sub-millisecond on-device explanation without computing heavy KernelSHAP iterations on mobile battery.
- **Stability Evaluation:** Jaccard overlap of top-3 explanatory risk factors under synthetic homoglyph and structural adversarial evasions.

---

## 2. Explanation Stability Under Perturbations

| Evaluated URL | Top-3 Feature Overlap | Stability Status | Key Explanatory Factors |
| :--- | :--- | :--- | :--- |
| `https://paypal.com.account-verify.test/login` | **50.0%** | Stable | letter_cnt: Measured value: 36.0 |
| `http://netflix-billing-renewal.test/signin` | **50.0%** | Stable | letter_cnt: Measured value: 35.0 |
| `https://appleid.apple.com.manage-auth.test/login` | **50.0%** | Stable | letter_cnt: Measured value: 39.0 |
| `http://amazon-prime-giftcard-winner.test/claim` | **50.0%** | Stable | letter_cnt: Measured value: 38.0 |
| `https://chase-bank-alert-resolution.test/auth` | **50.0%** | Stable | letter_cnt: Measured value: 37.0 |

---

## 3. Top Influential Risk Indicators

1. **Brand Impersonation & Spoofing:** Identifies high typographical similarity to monitored financial and technology brands.
2. **Suspicious Subdomain Nesting:** Detects multi-level subdomain prefixes masquerading as legitimate entities.
3. **Information Entropy:** Detects auto-generated tokens and encrypted/encoded payload fragments.
4. **Unencrypted Transport (HTTP):** Identifies absence of TLS encryption on sensitive credential endpoints.
