"""
Compact Student Model and Pure-Python Tree Inference Engine for Mobile Deployment.
Key Features:
1. Lightweight decision tree / ensemble representation stored in compact JSON.
2. Zero external dependencies: Does NOT require scikit-learn, C-extensions, or heavy packages.
3. Microsecond inference latency suitable for Android smartphones.
4. Deterministic and bit-identical inference between development environment and mobile APK.
"""

import json
import os
import math
from typing import Dict, List, Any, Union, Optional


class CompactTreeNode:
    """Represents a single decision node or leaf in a tree."""

    def __init__(
        self,
        feature_name: Optional[str] = None,
        threshold: Optional[float] = None,
        left: Optional['CompactTreeNode'] = None,
        right: Optional['CompactTreeNode'] = None,
        value: Optional[float] = None  # Class 1 probability or logit at leaf
    ):
        self.feature_name = feature_name
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    @property
    def is_leaf(self) -> bool:
        return self.value is not None

    def to_dict(self) -> Dict[str, Any]:
        if self.is_leaf:
            return {"value": self.value}
        return {
            "feature": self.feature_name,
            "threshold": self.threshold,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'CompactTreeNode':
        if "value" in d and d["value"] is not None:
            return CompactTreeNode(value=float(d["value"]))
        return CompactTreeNode(
            feature_name=d.get("feature"),
            threshold=float(d["threshold"]) if d.get("threshold") is not None else None,
            left=CompactTreeNode.from_dict(d["left"]) if d.get("left") else None,
            right=CompactTreeNode.from_dict(d["right"]) if d.get("right") else None
        )


class CompactEnsembleStudent:
    """
    Lightweight tree ensemble student model for mobile.
    Executes in pure Python without scikit-learn or native libraries.
    """

    def __init__(self, trees: Optional[List[CompactTreeNode]] = None, feature_names: Optional[List[str]] = None, weights: Optional[List[float]] = None):
        self.trees = trees or []
        self.feature_names = feature_names or []
        self.weights = weights or ([1.0 / len(self.trees)] * len(self.trees) if self.trees else [])

    def predict_tree(self, node: CompactTreeNode, features: Dict[str, float]) -> float:
        """Traverse a single tree to leaf."""
        curr = node
        while not curr.is_leaf:
            val = features.get(curr.feature_name, 0.0)
            if val <= curr.threshold:
                curr = curr.left
            else:
                curr = curr.right
            if curr is None:
                return 0.5
        return curr.value

    def predict_proba(self, features: Dict[str, float]) -> float:
        """
        Aggregate predictions across all trees to produce calibrated probability [0.0, 1.0].
        """
        if not self.trees:
            return 0.5

        total_weight = sum(self.weights)
        weighted_sum = sum(
            self.predict_tree(tree, features) * w for tree, w in zip(self.trees, self.weights)
        )
        prob = weighted_sum / total_weight if total_weight > 0 else 0.5
        return max(0.0, min(1.0, prob))

    def save_json(self, file_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Export model to compact JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        export_data = {
            "model_type": "CompactEnsembleStudent",
            "version": "1.0.0",
            "metadata": metadata or {},
            "feature_names": self.feature_names,
            "weights": self.weights,
            "trees": [tree.to_dict() for tree in self.trees]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

    @classmethod
    def load_json(cls, file_path: str) -> 'CompactEnsembleStudent':
        """Load student model from compact JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        trees = [CompactTreeNode.from_dict(t) for t in data["trees"]]
        feature_names = data.get("feature_names", [])
        weights = data.get("weights", [1.0 / len(trees)] * len(trees))
        return cls(trees=trees, feature_names=feature_names, weights=weights)
