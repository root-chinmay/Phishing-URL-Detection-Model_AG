"""
Shannon Entropy Analysis Module for MobiURL-Guard.
Computes information entropy for URLs and components:
- Full URL entropy
- Hostname entropy
- Domain entropy
- Path entropy
- Query string entropy
"""

import math
from collections import Counter
from typing import Dict


def calculate_shannon_entropy(text: str) -> float:
    """
    Compute Shannon entropy in bits per character.
    H(X) = - sum(P(x) * log2(P(x)))
    Returns 0.0 for empty strings.
    """
    if not text:
        return 0.0
    length = len(text)
    counts = Counter(text)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def extract_entropy_features(url: str, hostname: str = "", domain: str = "", path: str = "", query: str = "") -> Dict[str, float]:
    """
    Extract entropy features across all segments.
    """
    return {
        "entropy_url": calculate_shannon_entropy(url),
        "entropy_hostname": calculate_shannon_entropy(hostname),
        "entropy_domain": calculate_shannon_entropy(domain),
        "entropy_path": calculate_shannon_entropy(path),
        "entropy_query": calculate_shannon_entropy(query),
    }
