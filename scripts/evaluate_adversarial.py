"""
Adversarial Robustness Evaluation Script for MobiURL-Guard (Research Gap 4).
Evaluates clean vs adversarial detection quality across:
- Homoglyphs
- Typosquatting
- Subdomain injection
- Length padding
- Percent encoding
- Nested redirects
- Case randomization

Generates reports/adversarial_report.md.
"""

import os
import sys
import json
from typing import Dict, List, Any

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.security.adversarial import AdversarialURLEngine
from src.models.inference_engine import MobiURLInferenceEngine
from src.evaluation.classification_metrics import evaluate_classifier_performance


def run_adversarial_evaluation():
    print("[*] Starting Adversarial Robustness Evaluation...")
    engine = MobiURLInferenceEngine()
    adv_gen = AdversarialURLEngine(seed=42)

    # Controlled evaluation test cases (using test domains & known samples)
    test_urls = [
        ("https://paypal.com.account-verify.test/login", 1),
        ("http://192.168.1.100/secure/bank/login.php", 1),
        ("https://google.account-security-update.test/verify", 1),
        ("http://netflix-billing-renewal.test/signin", 1),
        ("https://appleid.apple.com.manage-auth.test/login", 1),
        ("http://amazon-prime-giftcard-winner.test/claim", 1),
        ("https://chase-bank-alert-resolution.test/auth", 1),
        ("http://binance-security-verification.test/wallet", 1),
        ("https://dhl-express-tracking-package.test/deliver", 1),
        ("http://microsoft-outlook-office365.test/login.aspx", 1),
        ("https://www.google.com/search?q=cybersecurity", 0),
        ("https://www.wikipedia.org/wiki/Phishing", 0),
        ("https://github.com/torvalds/linux", 0),
        ("https://www.microsoft.com/en-us/software-download", 0),
        ("https://www.apple.com/iphone-16-pro/", 0),
        ("https://www.amazon.com/gp/bestsellers", 0),
        ("https://www.netflix.com/browse", 0),
        ("https://www.paypal.com/us/home", 0),
        ("https://www.chase.com/personal/banking", 0),
        ("https://www.python.org/downloads/", 0),
    ]

    attack_types = [
        "clean",
        "homoglyph",
        "typosquat",
        "subdomain_injected",
        "padded",
        "percent_encoded",
        "nested_redirect",
        "case_randomized"
    ]

    attack_results = {}

    for attack in attack_types:
        y_true = []
        y_probs = []
        perturbed_urls = []

        for url, label in test_urls:
            if attack == "clean":
                p_url = url
            elif attack == "homoglyph":
                p_url = adv_gen.apply_homoglyphs(url)
            elif attack == "typosquat":
                p_url = adv_gen.apply_typosquatting(url)
            elif attack == "subdomain_injected":
                p_url = adv_gen.apply_subdomain_injection(url)
            elif attack == "padded":
                p_url = adv_gen.apply_url_padding(url)
            elif attack == "percent_encoded":
                p_url = adv_gen.apply_percent_encoding(url)
            elif attack == "nested_redirect":
                p_url = adv_gen.apply_nested_redirect(url)
            elif attack == "case_randomized":
                p_url = adv_gen.apply_case_randomization(url)

            pred = engine.predict(p_url)
            y_true.append(label)
            y_probs.append(pred["malicious_probability"])
            perturbed_urls.append(p_url)

        metrics = evaluate_classifier_performance(y_true, y_probs, threshold=0.50)
        attack_results[attack] = metrics

    clean_acc = attack_results["clean"]["accuracy"]
    clean_recall = attack_results["clean"]["recall"]

    print(f"[+] Baseline Clean Accuracy: {clean_acc:.4f} | Recall: {clean_recall:.4f}")
    for attack, m in attack_results.items():
        if attack == "clean":
            continue
        deg = clean_recall - m["recall"]
        print(f"    - {attack:<20}: Recall = {m['recall']:.4f} | Acc = {m['accuracy']:.4f} | Degradation = {deg:+.4f}")

    # Generate Markdown Adversarial Report
    report_md = f"""# Adversarial Robustness Evaluation Report: MobiURL-Guard (Research Gap 4)

## 1. Threat Model and Experimental Methodology
- **Adversary Capability:** Black-box query evasion via syntactic, lexical, encoding, and structural URL perturbations.
- **Controlled Environment:** All synthetic evaluations strictly execute on reserved `.test` domains (RFC 2606) with zero deployable malicious infrastructure.
- **Evaluation Set:** Paired benign and phishing URLs subjected to 7 systematic evasion strategies.

---

## 2. Attack-Specific Robustness Breakdown

| Evasion Transformation Strategy | Adversarial Recall | Accuracy | Precision | F1-Score | Robustness Degradation ($\\Delta$ Recall) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Clean Baseline** | **{clean_recall:.4f}** | **{clean_acc:.4f}** | {attack_results['clean']['precision']:.4f} | {attack_results['clean']['f1_score']:.4f} | **0.0000** |
"""
    for attack, m in attack_results.items():
        if attack == "clean":
            continue
        deg = clean_recall - m["recall"]
        report_md += f"| **{attack.replace('_', ' ').title()}** | {m['recall']:.4f} | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['f1_score']:.4f} | **{deg:+.4f}** |\n"

    report_md += f"""
---

## 3. Defense Analysis & Mitigations

1. **Homoglyph Invariance:** Unicode normalization and the confusable character detector flag Cyrillic/Greek character substitutions even when visually identical to Latin characters.
2. **Padding Resilience:** Multi-segment Shannon entropy and path/query ratio features decouple base URL representations from appended random padding.
3. **Subdomain Spoofing:** Brand impersonation detection analyzes registered domain boundaries independently from arbitrary prefix labels.
4. **Encoding Normalization:** URL canonicalization unquotes `%XX` hex sequences prior to feature extraction.
"""

    report_path = os.path.join("reports", "adversarial_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[+] Saved adversarial robustness report to: {report_path}")


if __name__ == "__main__":
    run_adversarial_evaluation()
