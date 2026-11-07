"""
Brand Impersonation Detection Engine for MobiURL-Guard (Research Gap 5).
Detects:
- Typographical similarity / Levenshtein distance against known brand domains
- Character n-gram similarity (Jaccard similarity on character 3-grams)
- Confusable domain spellings
- Brand name embedded in subdomains of third-party domains
- Brand name appearing in paths while host is an unrelated registrant
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute dynamic programming Levenshtein distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalized_similarity(s1: str, s2: str) -> float:
    """Normalized edit similarity in range [0, 1]."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return round(1.0 - (dist / max_len), 4)


def char_ngram_jaccard(s1: str, s2: str, n: int = 3) -> float:
    """Compute Jaccard similarity of character n-grams."""
    if len(s1) < n or len(s2) < n:
        return 1.0 if s1 == s2 else 0.0
    ngrams1 = {s1[i:i+n] for i in range(len(s1) - n + 1)}
    ngrams2 = {s2[i:i+n] for i in range(len(s2) - n + 1)}
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    return round(intersection / union if union > 0 else 0.0, 4)


class BrandImpersonationDetector:
    def __init__(self, config_path: Optional[str] = None):
        self.brands: List[Dict[str, Any]] = []
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.brands = data.get("brands", [])
        else:
            # Fallback default essential brands
            self.brands = [
                {"name": "Google", "official_domains": ["google.com", "gmail.com"], "aliases": ["google", "gmail"]},
                {"name": "Microsoft", "official_domains": ["microsoft.com", "live.com"], "aliases": ["microsoft", "office365", "outlook"]},
                {"name": "Apple", "official_domains": ["apple.com", "icloud.com"], "aliases": ["apple", "icloud"]},
                {"name": "PayPal", "official_domains": ["paypal.com"], "aliases": ["paypal"]},
                {"name": "Amazon", "official_domains": ["amazon.com"], "aliases": ["amazon"]},
                {"name": "Netflix", "official_domains": ["netflix.com"], "aliases": ["netflix"]},
                {"name": "Facebook", "official_domains": ["facebook.com", "fb.com"], "aliases": ["facebook", "meta"]},
                {"name": "Chase Bank", "official_domains": ["chase.com"], "aliases": ["chase"]},
            ]

    def analyze(self, domain: str, path: str = "", subdomains: str = "") -> Dict[str, Any]:
        """
        Analyze domain, subdomains, and path for brand impersonation features.
        """
        domain_clean = domain.lower().strip()
        subdom_clean = subdomains.lower().strip()
        path_clean = path.lower().strip()

        # Remove TLD for root domain check
        domain_parts = domain_clean.split(".")
        main_domain_label = domain_parts[0] if domain_parts else domain_clean

        max_lev_sim = 0.0
        max_ngram_sim = 0.0
        impersonated_brand = None
        brand_in_subdomain = False
        brand_in_path = False
        is_legitimate_brand_domain = False

        for b in self.brands:
            brand_name = b["name"]
            official_doms = [od.lower() for od in b.get("official_domains", [])]
            aliases = [a.lower() for a in b.get("aliases", [brand_name.lower()])]

            # Check if domain is actually official
            if domain_clean in official_doms or any(domain_clean.endswith("." + od) for od in official_doms):
                is_legitimate_brand_domain = True
                continue

            # Check similarity against official domain roots or aliases
            for alias in aliases:
                lev_sim = normalized_similarity(main_domain_label, alias)
                ngram_sim = char_ngram_jaccard(main_domain_label, alias)

                # If high similarity but not official -> typo/lookalike candidate
                if lev_sim > max_lev_sim:
                    max_lev_sim = lev_sim
                    if lev_sim > 0.75 and lev_sim < 1.0:
                        impersonated_brand = brand_name

                if ngram_sim > max_ngram_sim:
                    max_ngram_sim = ngram_sim

                # Check brand embedded in subdomains
                if alias in subdom_clean and not is_legitimate_brand_domain:
                    brand_in_subdomain = True
                    if not impersonated_brand:
                        impersonated_brand = brand_name

                # Check brand in path while on third-party domain
                if alias in path_clean and not is_legitimate_brand_domain:
                    brand_in_path = True
                    if not impersonated_brand:
                        impersonated_brand = brand_name

        is_impersonation_suspected = 1.0 if (
            (not is_legitimate_brand_domain) and (
                (max_lev_sim >= 0.80 and max_lev_sim < 1.0) or
                brand_in_subdomain or
                (brand_in_path and max_ngram_sim > 0.4)
            )
        ) else 0.0

        return {
            "brand_impersonation_score": max_lev_sim,
            "brand_ngram_similarity": max_ngram_sim,
            "brand_in_subdomain": 1.0 if brand_in_subdomain else 0.0,
            "brand_in_path": 1.0 if brand_in_path else 0.0,
            "is_impersonation_suspected": is_impersonation_suspected,
            "detected_target_brand": impersonated_brand or "None",
            "is_official_brand_domain": 1.0 if is_legitimate_brand_domain else 0.0,
        }
