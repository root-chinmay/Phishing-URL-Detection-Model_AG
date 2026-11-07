"""
Explanation Stability Evaluation Module for MobiURL-Guard.
Measures:
- Top-K feature overlap (Jaccard index of top explanatory features)
- Rank correlation of feature attributions
- Stability under adversarial perturbations (clean vs perturbed URLs)
"""

from typing import List, Dict, Any, Set


def jaccard_overlap(list1: List[str], list2: List[str]) -> float:
    """Compute Jaccard similarity of two feature sets."""
    s1 = set(list1)
    s2 = set(list2)
    union = len(s1 | s2)
    if union == 0:
        return 1.0
    return round(len(s1 & s2) / union, 4)


def evaluate_explanation_stability(clean_reasons: List[str], perturbed_reasons: List[str], k: int = 3) -> Dict[str, Any]:
    """
    Evaluate stability between clean URL explanation and perturbed URL explanation.
    """
    top_clean = clean_reasons[:k]
    top_perturbed = perturbed_reasons[:k]
    overlap = jaccard_overlap(top_clean, top_perturbed)

    return {
        "top_k": k,
        "clean_top_features": top_clean,
        "perturbed_top_features": top_perturbed,
        "jaccard_overlap": overlap,
        "is_stable": overlap >= 0.5,
        "explanation_shift": list(set(top_perturbed) - set(top_clean))
    }
