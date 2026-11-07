"""
Local Explainable AI (XAI) Engine for MobiURL-Guard (Research Gap 10).
Generates fast, interpretable, on-device explanations without heavy runtime dependencies.
Identifies top risk-increasing and risk-decreasing features for any URL prediction.
"""

from typing import Dict, List, Any, Tuple, Optional

# Human-readable labels and descriptions for features
FEATURE_DESCRIPTIONS = {
    "url_len": ("URL Length", "Excessive overall URL length often used to hide destinations or inject tokens"),
    "dom_len": ("Domain Length", "Unusually long domain name"),
    "is_ip": ("IP Address Host", "Direct IP address used instead of a legitimate registered domain"),
    "tld_len": ("TLD Length", "Unusual top-level domain structure"),
    "subdom_cnt": ("Subdomain Count", "High number of nested subdomains used for spoofing"),
    "letter_ratio": ("Letter Ratio", "Abnormal ratio of letters to total characters"),
    "digit_ratio": ("Digit Ratio", "High density of numeric digits in URL"),
    "spec_ratio": ("Special Character Ratio", "Dense usage of special symbols and delimiters"),
    "is_https": ("HTTPS Security", "Plaintext HTTP connection lacking TLS encryption"),
    "slash_cnt": ("Path Depth", "Excessive directory nesting"),
    "entropy": ("Information Entropy", "High randomness characteristic of auto-generated or obfuscated strings"),
    "path_len": ("Path Length", "Abnormally long directory path"),
    "query_len": ("Query Length", "Extensive query parameters used for tracking or payload passing"),
    "dot_cnt": ("Dot Count", "Multiple dots indicating complex subdomain spoofing"),
    "dash_cnt": ("Hyphen Count", "Multiple hyphens commonly found in typosquatting and fake brands"),
    "at_cnt": ("@ Symbol", "Usage of '@' symbol which can mislead browsers into ignoring prefix credentials"),
    "percent_cnt": ("Percent Encoding", "High density of '%XX' encoded characters hiding true content"),
    "encoded_char_cnt": ("Obfuscated Hex Sequences", "Hexadecimal escape sequences detected"),
    "keyword_hits": ("Phishing Keywords", "Presence of security, login, or financial credential keywords"),
    "is_shortener": ("URL Shortener", "Known redirection shortener service hiding true destination"),
    "is_suspicious_tld": ("High-Risk TLD", "TLD associated with elevated spam and malware campaign rates"),
    "embedded_domain_in_path": ("Embedded Domain in Path", "Legitimate-looking domain embedded inside path to deceive users"),
    "confusable_char_count": ("Confusable Characters", "Homoglyphs visually mimicking standard Latin characters"),
    "brand_impersonation_score": ("Brand Impersonation", "Typographical or lexical similarity to a recognized brand"),
    "is_impersonation_suspected": ("Suspected Brand Spoofing", "Strong indicators of targeted brand spoofing"),
    "is_punycode": ("Punycode Domain", "Internationalized domain name (IDN) with potential homograph attack")
}

# Baseline averages typical of benign URLs
BENIGN_BASELINES = {
    "url_len": 35.0,
    "dom_len": 14.0,
    "is_ip": 0.0,
    "subdom_cnt": 0.8,
    "dot_cnt": 2.0,
    "dash_cnt": 0.3,
    "digit_cnt": 1.2,
    "digit_ratio": 0.04,
    "spec_ratio": 0.20,
    "is_https": 1.0,
    "entropy": 3.8,
    "path_len": 12.0,
    "query_len": 0.0,
    "keyword_hits": 0.0,
    "is_shortener": 0.0,
    "brand_impersonation_score": 0.1,
    "is_impersonation_suspected": 0.0,
    "confusable_char_count": 0.0,
    "is_punycode": 0.0
}


class LocalExplainer:
    """
    Computes local feature importance and explanatory reasons for individual predictions.
    Works entirely offline on mobile and desktop devices.
    """

    def __init__(self, feature_weights: Optional[Dict[str, float]] = None):
        # Default directional feature weights calibrated from tree and logistic baselines
        self.weights = feature_weights or {
            "is_ip": 3.5,
            "is_impersonation_suspected": 3.0,
            "brand_impersonation_score": 2.5,
            "keyword_hits": 2.2,
            "is_shortener": 2.0,
            "confusable_char_count": 2.5,
            "is_punycode": 2.0,
            "embedded_domain_in_path": 2.0,
            "is_suspicious_tld": 1.8,
            "at_cnt": 2.5,
            "entropy": 1.5,
            "subdom_cnt": 1.4,
            "dash_cnt": 1.2,
            "dot_cnt": 1.1,
            "digit_ratio": 1.3,
            "url_len": 0.8,
            "path_len": 0.6,
            "query_len": 0.7,
            "is_https": -1.5,  # Having HTTPS slightly reduces suspiciousness, absence increases
        }

    def explain_instance(self, features: Dict[str, float], top_k: int = 4) -> Dict[str, Any]:
        """
        Explain why a prediction received its risk score.
        Returns top risk-increasing and risk-decreasing factors.
        """
        risk_contributors = []
        safety_contributors = []

        for fname, val in features.items():
            baseline = BENIGN_BASELINES.get(fname, 0.0)
            weight = self.weights.get(fname, 0.5)

            # Special case for is_https: 0 means no https (risk factor)
            if fname == "is_https":
                if val == 0.0:
                    impact = 1.8
                    risk_contributors.append({
                        "feature": fname,
                        "display_name": "Unencrypted Connection (HTTP)",
                        "impact": impact,
                        "description": "Plaintext HTTP connection lacking TLS encryption increases vulnerability"
                    })
                continue

            deviation = val - baseline
            impact = deviation * weight

            disp_name, desc = FEATURE_DESCRIPTIONS.get(fname, (fname, f"Measured value: {val}"))

            if impact > 0.4:
                risk_contributors.append({
                    "feature": fname,
                    "display_name": disp_name,
                    "impact": round(impact, 3),
                    "value": round(val, 2),
                    "description": desc
                })
            elif impact < -0.4:
                safety_contributors.append({
                    "feature": fname,
                    "display_name": disp_name,
                    "impact": round(impact, 3),
                    "value": round(val, 2),
                    "description": desc
                })

        risk_contributors.sort(key=lambda x: x["impact"], reverse=True)
        safety_contributors.sort(key=lambda x: x["impact"])

        top_reasons = [r["display_name"] + ": " + r["description"] for r in risk_contributors[:top_k]]
        if not top_reasons:
            top_reasons = ["URL characteristics conform closely to standard legitimate domain baselines"]

        return {
            "top_risk_factors": risk_contributors[:top_k],
            "top_safety_factors": safety_contributors[:top_k],
            "human_readable_reasons": top_reasons
        }
