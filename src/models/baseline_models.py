"""
Multi-Model Machine Learning Engine for MobiURL-Guard.
Fast, vectorized training using NumPy:
1. Logistic Regression
2. Gaussian Naive Bayes
3. Fast Decision Tree
4. Random Forest Ensemble

Exports compact trees directly into CompactEnsembleStudent for zero-dependency mobile inference.
"""

import math
import random
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

from src.distillation.student import CompactTreeNode, CompactEnsembleStudent


class BaseClassifierWrapper:
    def fit(self, X: List[List[float]], y: List[int]):
        raise NotImplementedError

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        raise NotImplementedError


class FastLogisticRegression(BaseClassifierWrapper):
    """Vectorized Logistic Regression via Gradient Descent."""

    def __init__(self, lr: float = 0.05, epochs: int = 150):
        self.lr = lr
        self.epochs = epochs
        self.weights: Optional[np.ndarray] = None
        self.bias: float = 0.0

    def fit(self, X: List[List[float]], y: List[int]):
        X_arr = np.array(X, dtype=np.float32)
        y_arr = np.array(y, dtype=np.float32)
        n, d = X_arr.shape

        self.weights = np.zeros(d, dtype=np.float32)
        self.bias = 0.0

        for _ in range(self.epochs):
            z = np.clip(np.dot(X_arr, self.weights) + self.bias, -20.0, 20.0)
            p = 1.0 / (1.0 + np.exp(-z))
            err = p - y_arr

            grad_w = np.dot(X_arr.T, err) / n
            grad_b = float(np.mean(err))

            self.weights -= self.lr * grad_w
            self.bias -= self.lr * grad_b

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        X_arr = np.array(X, dtype=np.float32)
        z = np.clip(np.dot(X_arr, self.weights) + self.bias, -20.0, 20.0)
        p = 1.0 / (1.0 + np.exp(-z))
        return [round(float(v), 4) for v in p]


class FastDecisionTree(BaseClassifierWrapper):
    """Fast Vectorized Decision Tree with Gini Splits."""

    def __init__(self, max_depth: int = 5, min_samples_split: int = 20):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root: Optional[CompactTreeNode] = None
        self.feature_names: List[str] = []

    def _gini(self, y: np.ndarray) -> float:
        n = len(y)
        if n == 0:
            return 0.0
        p1 = float(np.mean(y))
        return 1.0 - (p1**2 + (1.0 - p1)**2)

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> CompactTreeNode:
        n = len(y)
        p1 = float(np.mean(y)) if n > 0 else 0.5

        if depth >= self.max_depth or n < self.min_samples_split or p1 <= 1e-4 or p1 >= (1.0 - 1e-4):
            return CompactTreeNode(value=round(p1, 4))

        curr_gini = self._gini(y)
        best_gain = 0.0
        best_feat = None
        best_thresh = None

        n_samples, n_features = X.shape
        # Sample features if many
        feat_indices = list(range(n_features))

        for f in feat_indices:
            col = X[:, f]
            # Fast quantile percentiles as candidate splits
            thresholds = np.unique(np.percentile(col, [10, 25, 40, 50, 60, 75, 90]))

            for thresh in thresholds:
                left_mask = col <= thresh
                n_left = np.sum(left_mask)
                n_right = n - n_left

                if n_left < 5 or n_right < 5:
                    continue

                gini_left = self._gini(y[left_mask])
                gini_right = self._gini(y[~left_mask])
                gain = curr_gini - ((n_left / n) * gini_left + (n_right / n) * gini_right)

                if gain > best_gain:
                    best_gain = gain
                    best_feat = f
                    best_thresh = float(thresh)

        if best_feat is None or best_gain <= 1e-4:
            return CompactTreeNode(value=round(p1, 4))

        fname = self.feature_names[best_feat] if self.feature_names else f"f_{best_feat}"
        left_mask = X[:, best_feat] <= best_thresh

        left_node = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_node = self._build_tree(X[~left_mask], y[~left_mask], depth + 1)

        return CompactTreeNode(
            feature_name=fname,
            threshold=round(best_thresh, 4),
            left=left_node,
            right=right_node
        )

    def fit(self, X: List[List[float]], y: List[int], feature_names: Optional[List[str]] = None):
        X_arr = np.array(X, dtype=np.float32)
        y_arr = np.array(y, dtype=np.float32)
        self.feature_names = feature_names or [f"f_{i}" for i in range(X_arr.shape[1])]
        self.root = self._build_tree(X_arr, y_arr, depth=0)

    def predict_single(self, x: np.ndarray) -> float:
        curr = self.root
        while not curr.is_leaf:
            f_idx = self.feature_names.index(curr.feature_name)
            val = x[f_idx]
            if val <= curr.threshold:
                curr = curr.left
            else:
                curr = curr.right
            if curr is None:
                return 0.5
        return curr.value

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        X_arr = np.array(X, dtype=np.float32)
        return [round(self.predict_single(row), 4) for row in X_arr]


class FastRandomForest(BaseClassifierWrapper):
    """Fast Random Forest Ensemble."""

    def __init__(self, n_estimators: int = 5, max_depth: int = 5, seed: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.seed = seed
        self.trees: List[FastDecisionTree] = []
        self.feature_names: List[str] = []

    def fit(self, X: List[List[float]], y: List[int], feature_names: Optional[List[str]] = None):
        X_arr = np.array(X, dtype=np.float32)
        y_arr = np.array(y, dtype=np.float32)
        self.feature_names = feature_names or [f"f_{i}" for i in range(X_arr.shape[1])]
        self.trees = []

        np.random.seed(self.seed)
        n = len(X_arr)

        for i in range(self.n_estimators):
            boot_idx = np.random.choice(n, size=n, replace=True)
            tree = FastDecisionTree(max_depth=self.max_depth)
            tree.fit(X_arr[boot_idx].tolist(), y_arr[boot_idx].tolist(), feature_names=self.feature_names)
            self.trees.append(tree)

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        all_preds = np.array([t.predict_proba(X) for t in self.trees])
        mean_preds = np.mean(all_preds, axis=0)
        return [round(float(v), 4) for v in mean_preds]

    def to_compact_student(self, feature_names: List[str]) -> CompactEnsembleStudent:
        compact_trees = [t.root for t in self.trees if t.root is not None]
        return CompactEnsembleStudent(trees=compact_trees, feature_names=feature_names)
