"""
Leakage-Safe Dataset Splitting Engine for MobiURL-Guard.
Supports:
1. Four-way splitting: Train (70%), Validation (10%), Calibration (10%), Test (10%)
2. Domain-Disjoint Grouping: Prevents identical registered domains from leaking between partitions
3. Stratified Partitioning: Preserves benign/malicious class balance
4. Canonical URL deduplication to eliminate optimistic evaluation bias
"""

import random
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse


def canonicalize_url_str(u: str) -> str:
    """Canonicalize URL for deduplication."""
    if not u:
        return ""
    u = u.strip().lower()
    if u.startswith("https://"):
        u = u[8:]
    elif u.startswith("http://"):
        u = u[7:]
    if u.startswith("www."):
        u = u[4:]
    return u.rstrip("/")


class DataSplitter:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def deduplicate(self, records: List[Dict[str, Any]], url_col: str = "url") -> List[Dict[str, Any]]:
        """Remove duplicate URLs based on canonical representation."""
        seen = set()
        deduped = []
        for r in records:
            canon = canonicalize_url_str(r.get(url_col, ""))
            if canon and canon not in seen:
                seen.add(canon)
                deduped.append(r)
        return deduped

    def split_domain_disjoint(
        self,
        records: List[Dict[str, Any]],
        domain_col: str = "dom",
        url_col: str = "url",
        train_ratio: float = 0.70,
        val_ratio: float = 0.10,
        cal_ratio: float = 0.10,
        test_ratio: float = 0.10
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Partition dataset grouped by registered domain.
        Guarantees that no domain in the test or calibration set appears in the training set.
        """
        # Group records by domain
        domain_groups = defaultdict(list)
        for r in records:
            dom = r.get(domain_col)
            if not dom:
                # Fallback parse domain from URL
                u = r.get(url_col, "")
                parsed = urlparse(u if "://" in u else f"http://{u}")
                dom = parsed.netloc or "unknown_domain"
            domain_groups[dom.lower().strip()].append(r)

        unique_domains = list(domain_groups.keys())
        self.rng.shuffle(unique_domains)

        total_samples = len(records)
        target_train = int(total_samples * train_ratio)
        target_val = int(total_samples * val_ratio)
        target_cal = int(total_samples * cal_ratio)

        train_records, val_records, cal_records, test_records = [], [], [], []

        for dom in unique_domains:
            group = domain_groups[dom]
            if len(train_records) < target_train:
                train_records.extend(group)
            elif len(val_records) < target_val:
                val_records.extend(group)
            elif len(cal_records) < target_cal:
                cal_records.extend(group)
            else:
                test_records.extend(group)

        return train_records, val_records, cal_records, test_records

    def split_stratified(
        self,
        records: List[Dict[str, Any]],
        label_col: str = "label",
        train_ratio: float = 0.70,
        val_ratio: float = 0.10,
        cal_ratio: float = 0.10,
        test_ratio: float = 0.10
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Standard stratified 4-way random partition."""
        by_class = defaultdict(list)
        for r in records:
            lbl = int(float(r.get(label_col, 0)))
            by_class[lbl].append(r)

        train, val, cal, test = [], [], [], []

        for lbl, group in by_class.items():
            self.rng.shuffle(group)
            n = len(group)
            n_train = int(n * train_ratio)
            n_val = int(n * val_ratio)
            n_cal = int(n * cal_ratio)

            train.extend(group[:n_train])
            val.extend(group[n_train:n_train + n_val])
            cal.extend(group[n_train + n_val:n_train + n_val + n_cal])
            test.extend(group[n_train + n_val + n_cal:])

        self.rng.shuffle(train)
        self.rng.shuffle(val)
        self.rng.shuffle(cal)
        self.rng.shuffle(test)

        return train, val, cal, test
