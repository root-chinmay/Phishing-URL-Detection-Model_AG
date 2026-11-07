"""
Baseline Training and Comparative Evaluation Script for MobiURL-Guard.
Trains multiple baseline models on the provided URL dataset:
- Evaluates Accuracy, Precision, Recall, F1-Score, ROC-AUC, FPR, FNR, Latency
- Generates reports/model_comparison.md
- Exports the best compact student model to models/exported/best_student_model.json
"""

import os
import sys
import time
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Dict, Any, List

from src.data.loader import DatasetLoader
from src.data.validation import DataValidator
from src.data.splitting import DataSplitter
from src.data.preprocessing import DataPreprocessor
from src.models.baseline_models import (
    FastLogisticRegression,
    FastDecisionTree,
    FastRandomForest,
)
from src.evaluation.classification_metrics import evaluate_classifier_performance
from src.calibration.probability_calibration import CalibratedProbabilityEstimator, compute_ece_and_bins, compute_brier_score
from src.uncertainty.conformal import ConformalPredictor


def train_and_evaluate_baselines():
    print("[*] Starting MobiURL-Guard Multi-Model Training Pipeline...")
    loader = DatasetLoader()
    raw_records, headers = loader.load_raw_records()
    print(f"[+] Loaded {len(raw_records):,} raw records.")

    # Validate and filter
    clean_records, rejected = DataValidator.filter_clean_records(raw_records)
    print(f"[+] Validated records: {len(clean_records):,} (rejected: {rejected})")

    # Deduplicate canonical URLs
    splitter = DataSplitter(seed=42)
    deduped = splitter.deduplicate(clean_records)
    print(f"[+] Canonical deduplicated records: {len(deduped):,}")

    # Stratified sampling across the entire dataset (ensuring both benign and malicious classes)
    from collections import defaultdict
    by_class = defaultdict(list)
    for r in deduped:
        lbl = int(float(r["label"]))
        by_class[lbl].append(r)

    print(f"[*] Available deduplicated counts by class: Class 0: {len(by_class[0]):,}, Class 1: {len(by_class[1]):,}")

    # Sample 10,000 benign and 10,000 malicious for a balanced, high-power research benchmark (total 20,000)
    rng = splitter.rng
    sample_c0 = rng.sample(by_class[0], min(10000, len(by_class[0])))
    sample_c1 = rng.sample(by_class[1], min(10000, len(by_class[1])))
    sample_subset = sample_c0 + sample_c1
    rng.shuffle(sample_subset)
    print(f"[+] Balanced research subset selected: {len(sample_subset):,} samples ({len(sample_c0):,} benign, {len(sample_c1):,} malicious)")

    # 4-way split: 70% Train, 10% Val, 10% Calibration, 10% Test
    train_recs, val_recs, cal_recs, test_recs = splitter.split_stratified(
        sample_subset, train_ratio=0.70, val_ratio=0.10, cal_ratio=0.10, test_ratio=0.10
    )
    print(f"[+] Partitions created -> Train: {len(train_recs)}, Val: {len(val_recs)}, Cal: {len(cal_recs)}, Test: {len(test_recs)}")

    # Preprocess
    preprocessor = DataPreprocessor()
    feat_names = preprocessor.feature_names

    X_train, y_train, _ = preprocessor.process_records(train_recs)
    X_val, y_val, _ = preprocessor.process_records(val_recs)
    X_cal, y_cal, _ = preprocessor.process_records(cal_recs)
    X_test, y_test, _ = preprocessor.process_records(test_recs)

    # Models to train
    models = {
        "Logistic Regression": FastLogisticRegression(epochs=150, lr=0.08),
        "Decision Tree": FastDecisionTree(max_depth=6),
        "Random Forest Ensemble": FastRandomForest(n_estimators=5, max_depth=6),
    }

    results = {}
    best_f1 = -1.0
    best_model_name = ""
    best_model_obj = None

    for name, model in models.items():
        print(f"[*] Training {name}...")
        t0 = time.time()
        if hasattr(model, "fit"):
            if "feature_names" in model.fit.__code__.co_varnames:
                model.fit(X_train, y_train, feature_names=feat_names)
            else:
                model.fit(X_train, y_train)
        train_time = time.time() - t0

        # Inference timing on test set
        t_inf0 = time.time()
        probs_test = model.predict_proba(X_test)
        inf_time_per_url = (time.time() - t_inf0) / len(X_test) * 1000.0  # ms

        # Performance evaluation
        metrics = evaluate_classifier_performance(y_test, probs_test)
        metrics["training_time_sec"] = round(train_time, 2)
        metrics["inference_latency_ms"] = round(inf_time_per_url, 3)

        results[name] = {
            "metrics": metrics,
            "probs_test": probs_test,
            "model_obj": model
        }

        print(f"    -> F1: {metrics['f1_score']:.4f} | Acc: {metrics['accuracy']:.4f} | AUC: {metrics['roc_auc']:.4f} | Latency: {metrics['inference_latency_ms']} ms")

        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_model_name = name
            best_model_obj = model

    print(f"[+] Best Model Selected: {best_model_name} (F1: {best_f1:.4f})")

    # Export best model as CompactEnsembleStudent
    os.makedirs(os.path.join("models", "exported"), exist_ok=True)
    export_path = os.path.join("models", "exported", "best_student_model.json")

    if hasattr(best_model_obj, "to_compact_student"):
        student = best_model_obj.to_compact_student(feat_names)
    elif hasattr(best_model_obj, "root"):
        student = best_model_obj.root
    else:
        # Construct compact ensemble
        rf = models["Random Forest Ensemble"]
        student = rf.to_compact_student(feat_names)

    student.save_json(export_path, metadata={
        "best_model": best_model_name,
        "f1_score": best_f1,
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    })
    print(f"[+] Exported compact student model to: {export_path}")

    # Generate Markdown Comparison Report
    report_md = f"""# Multi-Model Benchmark and Evaluation Report: MobiURL-Guard

## 1. Experimental Methodology

- **Dataset Samples Evaluated:** {len(sample_subset):,}
- **Data Partitions:** Train (70%), Validation (10%), Calibration (10%), Test (10%)
- **Feature Space:** {len(feat_names)} lexical, structural, and entropy features
- **Evaluation Criteria:** Accuracy, Precision, Recall, F1-Score, ROC-AUC, FPR, FNR, Inference Latency

---

## 2. Model Performance Comparison

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | FPR | FNR | Training Time (s) | Inference Latency (ms/URL) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for name, data in results.items():
        m = data["metrics"]
        report_md += f"| **{name}** | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | **{m['f1_score']:.4f}** | {m['roc_auc']:.4f} | {m['fpr']:.4f} | {m['fnr']:.4f} | {m['training_time_sec']}s | {m['inference_latency_ms']} ms |\n"

    report_md += f"""
---

## 3. Best Model Selection & Distillation Rationale

- **Selected Architecture:** `{best_model_name}`
- **Test F1-Score:** `{best_f1:.4f}`
- **Inference Latency:** `{results[best_model_name]['metrics']['inference_latency_ms']} ms/URL`
- **Mobile Feasibility:** Model serialized to zero-dependency JSON tree structure (`best_student_model.json`), enabling instant, offline execution on mobile devices without native compilation or heavyweight runtime packages.
"""

    report_path = os.path.join("reports", "model_comparison.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[+] Saved model comparison report to: {report_path}")

    return results, best_model_name


if __name__ == "__main__":
    train_and_evaluate_baselines()
