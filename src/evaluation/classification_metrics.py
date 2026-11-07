"""
Classification Metrics Evaluation Engine for MobiURL-Guard.
Computes:
- Accuracy, Precision, Recall, F1-Score
- False Positive Rate (FPR), False Negative Rate (FNR)
- ROC-AUC and PR-AUC
- Confusion matrix (TP, FP, TN, FN)
"""

from typing import List, Dict, Any, Tuple


def compute_confusion_matrix(y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
    tp, fp, tn, fn = 0, 0, 0, 0
    for yt, yp in zip(y_true, y_pred):
        if yt == 1 and yp == 1:
            tp += 1
        elif yt == 0 and yp == 1:
            fp += 1
        elif yt == 0 and yp == 0:
            tn += 1
        elif yt == 1 and yp == 0:
            fn += 1
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn}


def compute_roc_auc(y_true: List[int], y_scores: List[float]) -> float:
    """Compute ROC-AUC via rank-sum (Wilcoxon-Mann-Whitney statistic)."""
    positives = [s for s, y in zip(y_scores, y_true) if y == 1]
    negatives = [s for s, y in zip(y_scores, y_true) if y == 0]
    n_pos = len(positives)
    n_neg = len(negatives)
    if n_pos == 0 or n_neg == 0:
        return 0.5

    # Pairwise comparison
    wins = 0.0
    for p in positives:
        for n in negatives:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5

    return round(wins / (n_pos * n_neg), 4)


def evaluate_classifier_performance(
    y_true: List[int],
    y_probs: List[float],
    threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Computes full comprehensive evaluation metrics.
    """
    n = len(y_true)
    if n == 0:
        return {}

    y_pred = [1 if p >= threshold else 0 for p in y_probs]
    cm = compute_confusion_matrix(y_true, y_pred)
    tp, fp, tn, fn = cm["TP"], cm["FP"], cm["TN"], cm["FN"]

    accuracy = (tp + tn) / n if n > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    roc_auc = compute_roc_auc(y_true, y_probs)

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
        "sample_count": n
    }
