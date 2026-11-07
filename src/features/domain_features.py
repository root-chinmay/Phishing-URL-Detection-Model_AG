"""
Domain and Structural Analysis Engine for MobiURL-Guard.
Extracts:
- Registered domain, TLD, and subdomain breakdown
- IP address host validation (IPv4 and IPv6)
- Domain hierarchy depth
- Suspicious domain composition (hyphens, digits, hex patterns)
- Known disposable / shortener domain indicators
- Embedded domain names in path
"""

import re
import ipaddress
from urllib.parse import urlparse
from typing import Dict, Any, Tuple

# Popular URL shorteners
KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "adf.ly", "bit.do", "cutt.ly", "rb.gy", "rebrand.ly", "t.ly", "shorturl.at",
    "tiny.cc", "v.gd", "clck.ru", "s.id", "soo.gd", "trib.al"
}

# Common TLDs
COMMON_TLDS = {
    "com", "org", "net", "edu", "gov", "mil", "io", "co", "ai", "app",
    "uk", "ca", "de", "jp", "fr", "au", "in", "cn", "ru", "br"
}

# Suspicious / high-abuse TLDs often seen in malicious campaigns
SUSPICIOUS_TLDS = {
    "top", "xyz", "club", "buzz", "click", "work", "cfd", "cam", "icu",
    "rest", "gq", "ml", "cf", "ga", "tk", "fit", "surf", "monster", "sbs"
}


def is_ip_address(host: str) -> bool:
    """Check if host is an IPv4 or IPv6 address."""
    if not host:
        return False
    # Strip port if present
    host = host.split(":")[0].strip("[]")
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def parse_domain_structure(hostname: str) -> Tuple[str, str, str]:
    """
    Splits hostname into (subdomains, registered_domain, tld).
    Works offline without external network or public suffix list dependencies.
    """
    if not hostname:
        return "", "", ""

    hostname = hostname.lower().strip()
    if is_ip_address(hostname):
        return "", hostname, ""

    parts = hostname.split(".")
    if len(parts) <= 1:
        return "", hostname, ""

    # Handle common two-part TLDs (e.g. .co.uk, .com.au, .edu.au, .co.in)
    if len(parts) >= 3 and parts[-1] in ["uk", "au", "in", "br", "za", "nz"] and parts[-2] in ["co", "com", "edu", "gov", "ac", "org", "net"]:
        tld = f"{parts[-2]}.{parts[-1]}"
        reg_domain = f"{parts[-3]}.{tld}"
        subdomain = ".".join(parts[:-3])
    else:
        tld = parts[-1]
        reg_domain = f"{parts[-2]}.{tld}" if len(parts) >= 2 else parts[0]
        subdomain = ".".join(parts[:-2])

    return subdomain, reg_domain, tld


def extract_domain_features(url: str, hostname: str = "", path: str = "") -> Dict[str, Any]:
    """
    Extract comprehensive domain-level features.
    """
    subdomain, reg_domain, tld = parse_domain_structure(hostname)

    is_ip = 1.0 if is_ip_address(hostname) else 0.0
    subdom_count = float(len(subdomain.split(".")) if subdomain else 0)
    hierarchy_depth = float(len(hostname.split(".")) if hostname else 0)

    # Check for shorteners
    is_shortener = 1.0 if (hostname.lower() in KNOWN_SHORTENERS or reg_domain.lower() in KNOWN_SHORTENERS) else 0.0

    # Suspicious TLD
    tld_clean = tld.lower().split(".")[-1] if tld else ""
    is_suspicious_tld = 1.0 if tld_clean in SUSPICIOUS_TLDS else 0.0

    # Domain composition
    hyphen_count = float(reg_domain.count("-"))
    digit_count = float(sum(c.isdigit() for c in reg_domain))
    has_hex = 1.0 if re.search(r"[0-9a-f]{8,}", reg_domain.lower()) else 0.0

    # Check if domain name is embedded in the URL path (common obfuscation tactic)
    embedded_domain_in_path = 0.0
    if path:
        path_lower = path.lower()
        if re.search(r"https?://", path_lower) or re.search(r"\.(com|net|org|edu|gov|xyz)/", path_lower):
            embedded_domain_in_path = 1.0

    return {
        "hostname": hostname,
        "registered_domain": reg_domain,
        "tld": tld,
        "subdomain": subdomain,
        "is_ip": is_ip,
        "domain_len": float(len(reg_domain)),
        "tld_len": float(len(tld)),
        "subdom_cnt": subdom_count,
        "hierarchy_depth": hierarchy_depth,
        "is_shortener": is_shortener,
        "is_suspicious_tld": is_suspicious_tld,
        "domain_hyphens": hyphen_count,
        "domain_digits": digit_count,
        "has_hex_pattern": has_hex,
        "embedded_domain_in_path": embedded_domain_in_path,
    }
