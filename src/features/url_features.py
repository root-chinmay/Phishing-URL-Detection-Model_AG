"""
Advanced URL Feature Extraction Engine for MobiURL-Guard.
Extracts:
1. Lexical features (lengths, character counts, ratios, symbol counts)
2. Domain and structure features (TLD, subdomains, IP host, hierarchy depth)
3. Information-theoretic entropy (Shannon entropy for URL, host, domain, path, query)
4. Unicode and Homoglyph anomalies (Punycode, confusables, mixed scripts)
5. Brand Impersonation indicators
6. Obfuscation & Redirection indicators
"""

import os
import re
import math
import string
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List, Optional

from src.features.domain_features import extract_domain_features, parse_domain_structure, is_ip_address
from src.features.entropy_features import extract_entropy_features, calculate_shannon_entropy
from src.features.unicode_features import analyze_unicode_and_homoglyphs
from src.features.brand_detection import BrandImpersonationDetector

# Phishing / high-risk keywords in URLs
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "update", "account", "banking", "signin",
    "wallet", "confirm", "security", "support", "service", "password",
    "credential", "recover", "authenticate", "billing", "token", "auth",
    "notification", "alert", "access", "manage", "appleid", "paypal", "netflix"
]

SPECIAL_CHARACTERS = set("!#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


class URLFeatureExtractor:
    """
    Independent, deterministic URL feature engineering engine.
    Ensures identical feature order and calculation across training, evaluation, and mobile runtime.
    """

    def __init__(self, brand_config_path: Optional[str] = None):
        self.brand_detector = BrandImpersonationDetector(brand_config_path)
        self.suspicious_keyword_patterns = [
            re.compile(rf"\b{kw}\b", re.IGNORECASE) for kw in SUSPICIOUS_KEYWORDS
        ]

    def extract_features(self, url: str) -> Dict[str, float]:
        """
        Extract numeric feature vector for model input.
        Guarantees purely numerical output suitable for ML classifiers.
        """
        raw_url = str(url).strip()
        
        # Ensure scheme for standard parsing if missing
        parse_target = raw_url
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw_url):
            parse_target = "http://" + raw_url

        try:
            parsed = urlparse(parse_target)
        except Exception:
            # Fallback for malformed URLs
            parsed = urlparse("http://invalid.invalid")

        hostname = parsed.hostname or ""
        path = parsed.path or ""
        query = parsed.query or ""

        # --- A. Lexical Features ---
        url_len = float(len(raw_url))
        path_len = float(len(path))
        query_len = float(len(query))

        letter_cnt = float(sum(c.isalpha() for c in raw_url))
        digit_cnt = float(sum(c.isdigit() for c in raw_url))
        special_cnt = float(sum(c in SPECIAL_CHARACTERS for c in raw_url))

        letter_ratio = (letter_cnt / url_len) if url_len > 0 else 0.0
        digit_ratio = (digit_cnt / url_len) if url_len > 0 else 0.0
        spec_ratio = (special_cnt / url_len) if url_len > 0 else 0.0

        dot_cnt = float(raw_url.count("."))
        dash_cnt = float(raw_url.count("-"))
        under_cnt = float(raw_url.count("_"))
        slash_cnt = float(raw_url.count("/"))
        eq_cnt = float(raw_url.count("="))
        qm_cnt = float(raw_url.count("?"))
        amp_cnt = float(raw_url.count("&"))
        at_cnt = float(raw_url.count("@"))
        percent_cnt = float(raw_url.count("%"))

        # Suspicious keyword hits
        url_lower = raw_url.lower()
        keyword_hits = float(sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower))

        # Query parameters and encoding
        param_cnt = float(len(parse_qs(query, keep_blank_values=True))) if query else 0.0
        encoded_char_cnt = float(len(re.findall(r"%[0-9a-fA-F]{2}", raw_url)))
        is_https = 1.0 if raw_url.lower().startswith("https://") else 0.0

        # --- B. Domain Features ---
        domain_feats = extract_domain_features(raw_url, hostname=hostname, path=path)
        dom_len = domain_feats["domain_len"]
        tld_len = domain_feats["tld_len"]
        is_ip = domain_feats["is_ip"]
        subdom_cnt = domain_feats["subdom_cnt"]
        hierarchy_depth = domain_feats["hierarchy_depth"]
        is_shortener = domain_feats["is_shortener"]
        is_suspicious_tld = domain_feats["is_suspicious_tld"]
        embedded_domain_in_path = domain_feats["embedded_domain_in_path"]

        # --- C. Entropy Analysis ---
        reg_domain = domain_feats["registered_domain"]
        entropy_feats = extract_entropy_features(raw_url, hostname=hostname, domain=reg_domain, path=path, query=query)
        entropy = entropy_feats["entropy_url"]

        # --- D. Unicode & Homoglyphs ---
        unicode_feats = analyze_unicode_and_homoglyphs(raw_url, hostname=hostname)

        # --- E. Brand Impersonation ---
        subdomain = domain_feats["subdomain"]
        brand_feats = self.brand_detector.analyze(domain=reg_domain, path=path, subdomains=subdomain)

        # Assemble strictly aligned feature dictionary
        features = {
            # Base dataset features (directly compatible with provided dataset)
            "url_len": url_len,
            "dom_len": dom_len,
            "is_ip": is_ip,
            "tld_len": tld_len,
            "subdom_cnt": subdom_cnt,
            "letter_cnt": letter_cnt,
            "digit_cnt": digit_cnt,
            "special_cnt": special_cnt,
            "eq_cnt": eq_cnt,
            "qm_cnt": qm_cnt,
            "amp_cnt": amp_cnt,
            "dot_cnt": dot_cnt,
            "dash_cnt": dash_cnt,
            "under_cnt": under_cnt,
            "letter_ratio": round(letter_ratio, 4),
            "digit_ratio": round(digit_ratio, 4),
            "spec_ratio": round(spec_ratio, 4),
            "is_https": is_https,
            "slash_cnt": slash_cnt,
            "entropy": round(entropy, 4),
            "path_len": path_len,
            "query_len": query_len,

            # Advanced research extensions
            "at_cnt": at_cnt,
            "percent_cnt": percent_cnt,
            "encoded_char_cnt": encoded_char_cnt,
            "param_cnt": param_cnt,
            "keyword_hits": keyword_hits,
            "hierarchy_depth": hierarchy_depth,
            "is_shortener": is_shortener,
            "is_suspicious_tld": is_suspicious_tld,
            "embedded_domain_in_path": embedded_domain_in_path,
            "entropy_domain": entropy_feats["entropy_domain"],
            "entropy_path": entropy_feats["entropy_path"],
            "is_punycode": unicode_feats["is_punycode"],
            "mixed_script": unicode_feats["mixed_script"],
            "confusable_char_count": unicode_feats["confusable_char_count"],
            "brand_impersonation_score": brand_feats["brand_impersonation_score"],
            "is_impersonation_suspected": brand_feats["is_impersonation_suspected"],
        }

        return features

    def get_feature_names(self) -> List[str]:
        """Return the fixed list of feature names in canonical order."""
        sample = self.extract_features("https://example.com")
        return list(sample.keys())

    def get_base_feature_names(self) -> List[str]:
        """Return the exact 22 features matching the provided raw dataset."""
        return [
            "url_len", "dom_len", "is_ip", "tld_len", "subdom_cnt", "letter_cnt",
            "digit_cnt", "special_cnt", "eq_cnt", "qm_cnt", "amp_cnt", "dot_cnt",
            "dash_cnt", "under_cnt", "letter_ratio", "digit_ratio", "spec_ratio",
            "is_https", "slash_cnt", "entropy", "path_len", "query_len"
        ]
