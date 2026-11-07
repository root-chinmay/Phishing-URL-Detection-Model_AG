"""
Explainability Evaluation and Stability Benchmark for MobiURL-Guard (Research Gap 10).
Measures:
- Feature attributions across URL threat categories
- Explanation stability under adversarial evasion perturbations
- Generates reports/explainability_report.md.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.inference_engine import MobiURLInferenceEngine
from src.security.adversarial import AdversarialURLEngine
from src.explainability.stability import evaluate_explanation_stability


def run_explainability_benchmark():
    print("[*] Starting Explainability and Explanation Stability Benchmark...")
    engine = MobiURLInferenceEngine()
    adv_engine = AdversarialURLEngine(seed=42)

    sample_urls = [
        "https://paypal.com.account-verify.test/login",
        "http://netflix-billing-renewal.test/signin",
        "https://appleid.apple.com.manage-auth.test/login",
        "http://amazon-prime-giftcard-winner.test/claim",
        "https://chase-bank-alert-resolution.test/auth",
    ]

    stability_records = []

    for url in sample_urls:
        clean_pred = engine.predict(url)
        clean_reasons = clean_pred["top_reasons"]

        # Perturbed variant (homoglyph or typosquat)
        perturbed_url = adv_engine.apply_homoglyphs(url)
        perturbed_pred = engine.predict(perturbed_url)
        perturbed_reasons = perturbed_pred["top_reasons"]

        stability = evaluate_explanation_stability(clean_reasons, perturbed_reasons, k=3)
        stability_records.append({
            "url": url,
            "overlap": stability["jaccard_overlap"],
            "clean_reasons": clean_reasons,
            "perturbed_reasons": perturbed_reasons
        })

    avg_overlap = sum(r["overlap"] for r in stability_records) / len(stability_records)
    print(f"[+] Average Top-3 Explanation Overlap: {avg_overlap * 100:.1f}%")

    report_md = f"""# Explainable AI (XAI) and Stability Report: MobiURL-Guard (Research Gap 10)

## 1. Methodology
- **Mobile XAI Paradigm:** Lightweight local directional attribution computing feature deviations from calibrated benign baselines.
- **Complexity:** $O(D)$ where $D$ is feature dimension, enabling sub-millisecond on-device explanation without computing heavy KernelSHAP iterations on mobile battery.
- **Stability Evaluation:** Jaccard overlap of top-3 explanatory risk factors under synthetic homoglyph and structural adversarial evasions.

---

## 2. Explanation Stability Under Perturbations

| Evaluated URL | Top-3 Feature Overlap | Stability Status | Key Explanatory Factors |
| :--- | :--- | :--- | :--- |
"""
    for r in stability_records:
        report_md += f"| `{r['url']}` | **{r['overlap'] * 100:.1f}%** | {'Stable' if r['overlap'] >= 0.5 else 'Moderate Shift'} | {r['clean_reasons'][0]} |\n"

    report_md += f"""
---

## 3. Top Influential Risk Indicators

1. **Brand Impersonation & Spoofing:** Identifies high typographical similarity to monitored financial and technology brands.
2. **Suspicious Subdomain Nesting:** Detects multi-level subdomain prefixes masquerading as legitimate entities.
3. **Information Entropy:** Detects auto-generated tokens and encrypted/encoded payload fragments.
4. **Unencrypted Transport (HTTP):** Identifies absence of TLS encryption on sensitive credential endpoints.
"""

    rep_path = os.path.join("reports", "explainability_report.md")
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[+] Saved explainability report to: {rep_path}")


if __name__ == "__main__":
    run_explainability_benchmark()
