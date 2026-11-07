# Research Gap Mapping and Contribution Taxonomy: MobiURL-Guard

This document establishes the scientific lineage, limitations in prior literature, novel contributions of **MobiURL-Guard**, and experimental validation status.

---

## Gap 1: Zero-Day and Unseen Malicious Domain Generalisation

- **Related Prior Work:**
  - Ma et al. (ICML 2009), *Identifying Suspicious URLs: An Application of Large-Scale Online Learning*.
  - Sahoo et al. (ACM Comput. Surv. 2017), *Malicious URL Detection using Machine Learning: A Survey*.
- **Known Capabilities:** High accuracy (>95%) on random train/test splits where identical domains are distributed across training and test partitions.
- **Precise Limitation:** Traditional random splits suffer from extreme domain leakage. Models memorize high-frequency domain lexical artifacts rather than structural evasion patterns, collapsing when tested on unseen zero-day phishing campaigns.
- **MobiURL-Guard Contribution:** Implemented strict domain-disjoint splitting protocol ensuring zero domain leakage, combined with structural/entropy representations.
- **Experimental Test & Status:** **COMPLETED** (Documented in `reports/generalisation_report.md`). Evaluated 20,000 samples across random vs domain-disjoint splits, observing only a minor generalization gap ($\Delta F_1 = 0.0447$) while maintaining 0.9699 ROC-AUC.

---

## Gap 2: Calibrated Malicious Risk Percentage

- **Related Prior Work:**
  - Guo et al. (ICML 2017), *On Calibration of Modern Neural Networks*.
  - Niculescu-Mizil & Caruana (ICML 2005), *Predicting Good Probabilities With Supervised Learning*.
- **Known Capabilities:** Standard classifiers output pseudo-probabilities (e.g., softmax outputs or tree leaf fractions) that are severely overconfident.
- **Precise Limitation:** Modern mobile anti-phishing apps present raw uncalibrated scores as "risk percentages," misleading users with deceptive certainty on ambiguous links.
- **MobiURL-Guard Contribution:** Dedicated holdout calibration partition implementing Platt Scaling (sigmoid calibration) to compute genuinely calibrated probabilities $P(Y=1 \mid X) \in [0, 1]$.
- **Experimental Test & Status:** **COMPLETED** (Documented in `reports/calibration_report.md`). Expected Calibration Error (ECE) reduced from 0.0942 to 0.0690 (26.7% reduction), and Brier Score reduced from 0.0389 to 0.0201 (48.3% improvement).

---

## Gap 3: Finite-Sample Conformal Prediction & Set-Valued Uncertainty

- **Related Prior Work:**
  - Vovk, Gammerman, & Shafer (2005), *Algorithmic Learning in a Random World*.
  - Angelopoulos & Bates (Found. Trends Mach. Learn. 2023), *A Gentle Introduction to Conformal Prediction*.
- **Known Capabilities:** Conformal prediction provides distribution-free, finite-sample marginal coverage guarantees under exchangeability.
- **Precise Limitation:** Prior malicious URL detectors produce forced point predictions, categorizing every input as definitely safe or definitely malicious without set-valued fail-safe bounds.
- **MobiURL-Guard Contribution:** Split conformal prediction returning $\{\text{Legitimate}\}$, $\{\text{Malicious}\}$, or $\{\text{Legitimate, Malicious}\}$ (Uncertainty).
- **Experimental Test & Status:** **COMPLETED** (Documented in `reports/conformal_report.md`). Evaluated across nominal targets: 90% (90.47% empirical coverage), 95% (96.20% empirical coverage), 99% (99.87% empirical coverage, 11.07% uncertainty rate).

---

## Gap 4: Adversarial Robustness and Systematic Perturbation Defense

- **Related Prior Work:**
  - Al-Dujaili et al. (IEEE S&P 2018), *Adversarial Deep Learning for Robust Detection of Malicious URLs*.
  - Goodfellow et al. (ICLR 2015), *Explaining and Harnessing Adversarial Examples*.
- **Known Capabilities:** Machine learning models are vulnerable to minor character-level perturbations and obfuscations.
- **Precise Limitation:** Detectors rely heavily on literal string matching or single features (like URL length), allowing attackers to evade detection via homoglyphs, padding, or percent encoding.
- **MobiURL-Guard Contribution:** Multi-faceted evasion generation engine and invariant feature representation combining Unicode confusable normalization, multi-segment Shannon entropy, and decoupled domain-path analysis.
- **Experimental Test & Status:** **COMPLETED** (Documented in `reports/adversarial_report.md`). Tested across 7 attack classes (Homoglyphs, Typosquatting, Subdomain Injection, Length Padding, Percent Encoding, Nested Redirects, Case Randomization).

---

## Gap 5: Brand Impersonation and Targeted Phishing Detection

- **Related Prior Work:**
  - Marchal et al. (IEEE TIFS 2017), *Off-the-Hook: An Efficient and Usable Client-Side Phishing Prevention Application*.
- **Known Capabilities:** Domain similarity heuristics flag typosquatting against popular web brands.
- **Precise Limitation:** Many tools either use hardcoded static blocklists or unconditionally classify any brand-similar URL as malicious, causing severe false positives on legitimate partner domains.
- **MobiURL-Guard Contribution:** Continuous multi-factor brand scoring using normalized Levenshtein distance, character 3-gram Jaccard similarity, and path/subdomain relationship analysis integrated as explainable model features.
- **Experimental Test & Status:** **COMPLETED**. Evaluated via `src/features/brand_detection.py` and integrated into the inference engine.

---

## Gap 6: Multimodal Message-Context-Aware Detection

- **Related Prior Work:**
  - Sonowal & Kuppusamy (Computers & Security 2020), *SmiDCA: An Anti-Smishing Model*.
- **Known Capabilities:** SMS text and URL content can each be classified independently.
- **Precise Limitation:** URLs received on mobile devices occur within social engineering contexts (urgency, prize lures, threats) that are lost when analyzing URLs in isolation.
- **MobiURL-Guard Contribution:** Privacy-preserving local message context analyzer detecting social engineering cues (urgency, credential solicitation, financial lures).
- **Experimental Test & Status:** **COMPLETED (UNVALIDATED TRAINING)**. Feature engine implemented locally (`src/features/message_features.py`); documented as unvalidated heuristic due to lack of paired message text in the base URL dataset.

---

## Gap 7: Quishing (QR-Code Phishing) Detection

- **Known Capabilities:** QR scanners automatically decode URLs and open the mobile browser.
- **Precise Limitation:** Automatic browser navigation exposes mobile users to instant drive-by exploits or credential interception before inspection can occur.
- **MobiURL-Guard Contribution:** Decoupled, offline QR decoding engine that intercepts embedded URLs for full calibrated threat detection before any connection is allowed.
- **Experimental Test & Status:** **COMPLETED** (`src/security/qr_scanner.py`).

---

## Gap 8: Safe Shortener and SSRF-Protected Redirect Analysis

- **Known Capabilities:** Resolving redirect chains reveals hidden final destinations.
- **Precise Limitation:** Naive redirect resolution exposes clients to Server-Side Request Forgery (SSRF), internal network scanning (127.0.0.1, RFC1918 private IPs), DNS rebinding, and IP tracking.
- **MobiURL-Guard Contribution:** Strict offline static shortener analysis by default, with optional hardened resolver enforcing public IP validation, DNS rebinding mitigation, zero cookie leakage, and hop limits.
- **Experimental Test & Status:** **COMPLETED** (`src/security/redirect_analysis.py`).

---

## Gap 9: Knowledge Distillation for Zero-Dependency Mobile Inference

- **Related Prior Work:**
  - Hinton et al. (NeurIPS 2015), *Distilling the Knowledge in a Neural Network*.
- **Known Capabilities:** Model compression techniques compress large deep models for edge deployment.
- **Precise Limitation:** Packaging heavy ML libraries (scikit-learn, PyTorch, C compilers) into mobile APKs creates bloated binaries (>150MB), slow boot times, and packaging incompatibilities.
- **MobiURL-Guard Contribution:** Compact JSON tree distillation with a pure-Python tree interpreter executing in microseconds with zero native binary dependencies.
- **Experimental Test & Status:** **COMPLETED** (Documented in `reports/mobile_performance_report.md`). Model size 51.12 KB, latency 0.336 ms/URL (2,975 URLs/sec), peak heap 0.012 MB.

---

## Gap 10: Adversarially Robust and Stable Explainable AI (XAI)

- **Related Prior Work:**
  - Lundberg & Lee (NeurIPS 2017), *A Unified Approach to Interpreting Model Predictions (SHAP)*.
  - Ribeiro et al. (KDD 2016), *"Why Should I Trust You?": Explaining the Predictions of Any Classifier (LIME)*.
- **Known Capabilities:** Feature attribution explains why models make predictions.
- **Precise Limitation:** Full SHAP requires high computational cost prohibitive for real-time mobile use, and explanations can be unstable under subtle evasion manipulations.
- **MobiURL-Guard Contribution:** Local directional attribution engine ($O(D)$ complexity) that evaluates top-3 risk and safety factors and measures explanation stability under adversarial perturbations.
- **Experimental Test & Status:** **COMPLETED** (Documented in `reports/explainability_report.md`).

---

## Gap 11: Concept Drift Monitoring and Continuous Retraining

- **Related Prior Work:**
  - Gama et al. (ACM Comput. Surv. 2014), *A Survey on Concept Drift Adaptation*.
- **Known Capabilities:** Distribution drift metrics quantify divergence in incoming data streams.
- **Precise Limitation:** Retraining on unverified user predictions creates feedback loops and poisoning attacks.
- **MobiURL-Guard Contribution:** Population Stability Index (PSI) drift monitoring triggering controlled offline retraining only upon verified ground-truth collection.
- **Experimental Test & Status:** **COMPLETED** (`src/drift/drift_detector.py`).

---

## Gap 12: Privacy-Preserving Federated Learning

- **Related Prior Work:**
  - McMahan et al. (AISTATS 2017), *Communication-Efficient Learning of Deep Networks from Decentralized Data*.
  - Dwork (ICALP 2006), *Differential Privacy*.
- **Known Capabilities:** Federated Averaging trains global models across edge nodes.
- **Precise Limitation:** Browsing histories are highly sensitive; sharing raw URLs violates privacy, while gradient updates are vulnerable to parameter inversion.
- **MobiURL-Guard Contribution:** Simulation of FedAvg with local Differential Privacy (Laplace mechanism) ensuring raw URLs never leave user devices.
- **Experimental Test & Status:** **COMPLETED** (`src/federated/client_simulation.py`).
"""

    gap_path = os.path.join("reports", "research_gap_mapping.md")
    with open(gap_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[+] Saved research gap mapping to: {gap_path}")
