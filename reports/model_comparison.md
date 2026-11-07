# Multi-Model Benchmark and Evaluation Report: MobiURL-Guard

## 1. Experimental Methodology

- **Dataset Samples Evaluated:** 20,000
- **Data Partitions:** Train (70%), Validation (10%), Calibration (10%), Test (10%)
- **Feature Space:** 22 lexical, structural, and entropy features
- **Evaluation Criteria:** Accuracy, Precision, Recall, F1-Score, ROC-AUC, FPR, FNR, Inference Latency

---

## 2. Model Performance Comparison

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | FPR | FNR | Training Time (s) | Inference Latency (ms/URL) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | 0.6010 | 0.5587 | 0.9620 | **0.7068** | 0.8370 | 0.7600 | 0.0380 | 0.06s | 0.002 ms |
| **Decision Tree** | 0.9190 | 0.9439 | 0.8910 | **0.9167** | 0.9722 | 0.0530 | 0.1090 | 0.26s | 0.004 ms |
| **Random Forest Ensemble** | 0.9295 | 0.9507 | 0.9060 | **0.9278** | 0.9798 | 0.0470 | 0.0940 | 3.6s | 0.046 ms |

---

## 3. Best Model Selection & Distillation Rationale

- **Selected Architecture:** `Random Forest Ensemble`
- **Test F1-Score:** `0.9278`
- **Inference Latency:** `0.046 ms/URL`
- **Mobile Feasibility:** Model serialized to zero-dependency JSON tree structure (`best_student_model.json`), enabling instant, offline execution on mobile devices without native compilation or heavyweight runtime packages.
