# MobiURL-Guard: Explainable, Calibrated, Adversarially Robust and Privacy-Aware Mobile Malicious URL Detection Framework

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passed-brightgreen.svg)](tests/)
[![Offline Engine](https://img.shields.io/badge/Execution-100%25%20On--Device%20Offline-success.svg)](#on-device-mobile-architecture)

> **Research Internship & Experimental Paper Implementation**  
> **Author / Lead Researcher:** Chinmay Amodkar  
> **Repository:** [Phishing-URL-Detection-Model](https://github.com/root-chinmay/Phishing-URL-Detection-Model.git)

---

## 1. Executive Summary & Research Abstract

Mobile devices are the primary vector for modern credential harvesting, smishing, and malicious redirection campaigns. Existing mobile protections suffer from four critical deficiencies:
1. **Uncalibrated Certainty:** Classifiers output deceptive overconfident probabilities rather than calibrated risks.
2. **Forced Point Decisions:** Absence of set-valued uncertainty quantification fails to flag ambiguous zero-day URLs.
3. **Domain Leakage:** Conventional train/test splits overestimate real-world detection by leaking high-frequency domains across partitions.
4. **Heavy Cloud Dependencies:** Many systems require remote API lookups that violate mobile user privacy and fail without network connectivity.

**MobiURL-Guard** resolves these gaps with a research-grade, privacy-preserving defensive framework. Key capabilities:
- **Calibrated Risk Percentage (0% to 100%):** Platt Sigmoid scaling reduces Expected Calibration Error (ECE) from 0.0942 to 0.0690 (26.7% reduction).
- **Split Conformal Prediction:** Rigorous finite-sample marginal coverage guarantees (90%, 95%, 99%) yielding set-valued predictions: `{Legitimate}`, `{Malicious}`, or `{Legitimate, Malicious}` (Uncertainty).
- **Zero-Day Generalisation:** Tested on strict domain-disjoint partitions (zero domain leakage) achieving 0.9027 accuracy and 0.9699 ROC-AUC on completely unseen domains.
- **Microsecond On-Device Mobile Engine:** Distilled into a zero-dependency compact JSON decision ensemble running at **0.336 ms/URL** (2,975 URLs/sec) with a 51 KB model footprint and zero remote data transmission.

---

## 2. Experimental Research Results

All metrics reported below were experimentally measured on the provided 116,600-record URL dataset (`data/raw/dataset.csv`).

### A. Multi-Model Benchmark (`reports/model_comparison.md`)
Evaluated on 20,000 balanced, canonical-deduplicated samples (Train: 70%, Val: 10%, Cal: 10%, Test: 10%):

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Latency (ms/URL) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Fast Logistic Regression** | 60.10% | 55.43% | 97.40% | 0.7068 | 0.8370 | 0.002 ms |
| **Fast Decision Tree** | 91.90% | 91.50% | 91.85% | 0.9167 | 0.9722 | 0.004 ms |
| **Random Forest Ensemble (Best)** | **92.95%** | **92.60%** | **92.95%** | **0.9278** | **0.9798** | **0.046 ms** |

### B. Probability Calibration & Conformal Bounds (`reports/calibration_report.md` & `reports/conformal_report.md`)
Fitted on a dedicated holdout calibration partition ($N_{cal} = 1,500$):
- **Expected Calibration Error (ECE):** Reduced from **0.0942** to **0.0690** (26.7% reduction).
- **Brier Score:** Reduced from **0.0389** to **0.0201** (48.3% improvement).
- **Conformal Coverage:**
  - Nominal 90% ($\alpha=0.10$): **90.47%** Empirical Coverage | Average Set Size: 0.913
  - Nominal 95% ($\alpha=0.05$): **96.20%** Empirical Coverage | Average Set Size: 0.975
  - Nominal 99% ($\alpha=0.01$): **99.87%** Empirical Coverage | Uncertainty Rate: 11.07%

### C. Zero-Day Generalisation Comparison (`reports/generalisation_report.md`)
- **Random Stratified Split:** Accuracy = 92.95%, F1 = 0.9278, ROC-AUC = 0.9798
- **Domain-Disjoint Split (Zero Domain Overlap):** Accuracy = 90.27%, F1 = 0.8831, ROC-AUC = 0.9699
- **Generalisation Gap:** $\Delta F_1 = 0.0447$. Confirms strong structural feature generalisation to unseen zero-day domains.

### D. Mobile Inference Performance (`reports/mobile_performance_report.md`)
- **Model Artefact Size:** **51.12 KB** (Compact JSON tree structure).
- **Inference Latency:** **0.336 ms / URL** (2,975 URLs/sec).
- **Engine Startup Time:** **2.08 ms**.
- **RAM / Heap Allocation:** **0.012 MB**.
- **Offline Reliability:** 100% on-device (Zero network calls required).

---

## 3. Project Directory Architecture

```
URL_Threat_Detection/
├── README.md                           # Master Research & Engineering Documentation
├── requirements.txt                     # Production dependencies
├── pyproject.toml                      # Build and test specifications
├── vercel.json                         # Vercel serverless deployment config
├── buildozer.spec                      # Android packaging specification
├── config/
│   ├── dataset_config.yaml             # Configurable dataset ingestion schema
│   ├── model_config.yaml               # Training and evaluation parameters
│   └── brand_domains.json              # Local reference brand database
├── data/
│   ├── raw/dataset.csv                 # Audited 116,600-record dataset
│   ├── processed/                      # Cleaned partitions
│   └── adversarial/                    # Synthetic adversarial test suites
├── api/
│   └── index.py                        # Vercel FastAPI serverless API & Web Dashboard
├── src/
│   ├── features/
│   │   ├── url_features.py             # 22+ advanced lexical and structural features
│   │   ├── domain_features.py          # TLD, subdomain, and shortener analysis
│   │   ├── entropy_features.py         # Shannon entropy across URL segments
│   │   ├── unicode_features.py         # Punycode & homoglyph confusable analysis
│   │   ├── brand_detection.py          # Levenshtein & 3-gram brand spoofing detector
│   │   └── message_features.py         # Multimodal SMS/WhatsApp context analyzer
│   ├── models/
│   │   ├── baseline_models.py          # Fast vectorized classifiers
│   │   └── inference_engine.py         # Unified end-to-end prediction engine
│   ├── calibration/
│   │   └── probability_calibration.py  # Platt Scaling, ECE, Brier score
│   ├── uncertainty/
│   │   ├── conformal.py                # Split Conformal Prediction engine
│   │   └── out_of_distribution.py      # OOD & Mahalanobis distance evaluation
│   ├── security/
│   │   ├── adversarial.py              # Synthetic URL evasion generator
│   │   ├── qr_scanner.py               # Quishing / QR code decoder
│   │   └── redirect_analysis.py        # SSRF-protected safe redirect analyzer
│   ├── explainability/
│   │   ├── local_explainer.py          # Fast on-device directional attribution
│   │   └── stability.py                # Explanation stability under evasion
│   ├── distillation/
│   │   └── student.py                  # Pure-Python JSON tree interpreter
│   ├── drift/
│   │   └── drift_detector.py           # PSI and continuous monitoring
│   ├── federated/
│   │   └── client_simulation.py        # FedAvg with Differential Privacy
│   └── mobile/
│       ├── main.py                     # Kivy Android application entrypoint
│       ├── screens.py                  # 6 full programmatic Python screens
│       ├── theme.py                    # Dark-mode cybersecurity design tokens
│       └── local_storage.py            # Opt-in privacy-first scan history
├── scripts/
│   ├── audit_dataset.py                # Exploratory dataset auditor
│   ├── train_baselines.py              # Multi-model training and export
│   ├── calibrate_model.py              # Probability calibration & conformal pipeline
│   ├── evaluate_adversarial.py         # Adversarial robustness evaluation
│   ├── evaluate_generalisation.py      # Zero-day cross-domain benchmark
│   ├── evaluate_explainability.py      # XAI stability evaluation
│   ├── benchmark_mobile.py             # Mobile latency and footprint benchmark
│   └── run_desktop_app.py              # Desktop interactive GUI / CLI runner
├── models/
│   ├── exported/best_student_model.json# Distilled zero-dependency mobile model
│   └── manifests/calibration_manifest.json# Fitted calibration parameters
├── reports/                            # Markdown experimental research reports
└── tests/                              # Comprehensive pytest test suite (19 tests)
```

---

## 4. Execution and Verification Guide

### Step 1: Environment Setup
```powershell
# Clone the repository
git clone https://github.com/root-chinmay/Phishing-URL-Detection-Model.git
cd Phishing-URL-Detection-Model

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Audit Dataset
Audits the raw 116,600-record dataset for duplicates, missing values, schemes, and potential leakage:
```powershell
python scripts/audit_dataset.py
```
*Outputs: `reports/dataset_audit_report.md` and `reports/dataset_statistics.json`*

### Step 3: Train Multi-Model Baselines & Distill Student Model
Trains Logistic Regression, Decision Trees, and Random Forest on balanced, deduplicated partitions:
```powershell
python scripts/train_baselines.py
```
*Outputs: `models/exported/best_student_model.json` and `reports/model_comparison.md`*

### Step 4: Calibrate Probabilities and Fit Conformal Bounds
Fits Platt Scaling and Conformal Quantiles strictly on the holdout calibration partition:
```powershell
python scripts/calibrate_model.py
```
*Outputs: `models/manifests/calibration_manifest.json`, `reports/calibration_report.md`, `reports/conformal_report.md`*

### Step 5: Evaluate Adversarial Robustness
Tests resilience across Homoglyphs, Typosquatting, Padding, Encoding, and Redirects:
```powershell
python scripts/evaluate_adversarial.py
```
*Outputs: `reports/adversarial_report.md`*

### Step 6: Evaluate Cross-Domain Generalisation
Tests domain-disjoint performance (zero domain leakage):
```powershell
python scripts/evaluate_generalisation.py
```
*Outputs: `reports/generalisation_report.md`*

### Step 7: Benchmark Mobile Performance
Measures latency, RAM usage, and startup time across 1,000 iterations:
```powershell
python scripts/benchmark_mobile.py
```
*Outputs: `reports/mobile_performance_report.md`*

### Step 8: Run Automated Test Suite
```powershell
python -m pytest tests/
```
*Output: 19 passed in 0.10s (100% pass rate).*

---

## 5. Mobile Application and Packaging

### Running on Desktop (Emulation Mode)
```powershell
python scripts/run_desktop_app.py
```
Launches the full interactive detection engine with live threat breakdown, conformal prediction sets, and explainable AI reasons.

### Packaging Android APK via Buildozer (WSL2 / Ubuntu)
To package into an Android APK (`.apk`):
```bash
# Inside WSL2 Ubuntu or Linux environment:
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

pip install --upgrade buildozer cython

# Generate Android APK:
buildozer -v android debug
```
The compiled APK will be output to `bin/mobiurlguard-1.0.0-arm64-v8a-debug.apk`.

---

## 6. Vercel Cloud Deployment

The repository includes a production-ready Vercel serverless configuration (`vercel.json` + `api/index.py`):
1. Connect this GitHub repository ([Phishing-URL-Detection-Model](https://github.com/root-chinmay/Phishing-URL-Detection-Model.git)) to [Vercel](https://vercel.com).
2. Vercel automatically detects `vercel.json` and `api/index.py`.
3. Enjoy an instant, interactive cloud API and cybersecurity web dashboard!

---

## 7. License and Citation

Licensed under the Apache License 2.0. If utilizing MobiURL-Guard for academic research, please cite:
```bibtex
@misc{amodkar2026mobiurlguard,
  author = {Amodkar, Chinmay},
  title = {MobiURL-Guard: An Explainable, Calibrated, Adversarially Robust and Privacy-Aware Mobile Malicious URL Detection Framework},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\\url{https://github.com/root-chinmay/Phishing-URL-Detection-Model}}
}
```
