"""
Unicode and Homoglyph Detection Module for MobiURL-Guard.
Detects:
- Punycode / IDN domains (xn--)
- Mixed script usage (Latin + Cyrillic / Greek)
- Unicode confusable characters
- Unicode normalization anomalies
"""

import unicodedata
import re
from typing import Dict, Tuple, Set


# Common confusable map (Cyrillic/Greek to Latin lookalikes)
CONFUSABLES = {
    '\u0430': 'a', '\u0435': 'e', '\u043e': 'o', '\u0440': 'p', '\u0441': 'c',
    '\u0443': 'y', '\u0445': 'x', '\u0456': 'i', '\u0458': 'j', '\u0410': 'A',
    '\u0412': 'B', '\u0415': 'E', '\u041a': 'K', '\u041c': 'M', '\u041d': 'H',
    '\u041e': 'O', '\u0420': 'P', '\u0421': 'C', '\u0422': 'T', '\u0425': 'X',
    '\u03bf': 'o', '\u03c1': 'p', '\u03b1': 'a', '\u03bd': 'v', '\u039f': 'O',
}


def get_character_script(char: str) -> str:
    """Identify the Unicode script of a single character."""
    name = unicodedata.name(char, "")
    if "CYRILLIC" in name:
        return "Cyrillic"
    elif "GREEK" in name:
        return "Greek"
    elif "ARABIC" in name:
        return "Arabic"
    elif "HEBREW" in name:
        return "Hebrew"
    elif "LATIN" in name:
        return "Latin"
    elif "DIGIT" in name or char.isdigit():
        return "Common"
    else:
        return "Other"


def analyze_unicode_and_homoglyphs(url: str, hostname: str = "") -> Dict[str, float]:
    """
    Extract homoglyph, punycode, and mixed-script features.
    """
    target = hostname if hostname else url
    
    is_punycode = 1.0 if "xn--" in target.lower() else 0.0
    
    # Try decoding punycode if present
    decoded_target = target
    if is_punycode:
        try:
            decoded_target = target.encode("ascii").decode("idna")
        except Exception:
            pass

    scripts: Set[str] = set()
    confusable_count = 0
    non_ascii_count = 0

    for ch in decoded_target:
        if ord(ch) > 127:
            non_ascii_count += 1
        if ch in CONFUSABLES:
            confusable_count += 1
        script = get_character_script(ch)
        if script not in ["Common", "Other"]:
            scripts.add(script)

    # Mixed script is flagged if more than 1 distinct alphabet is mixed (e.g. Latin + Cyrillic)
    mixed_script = 1.0 if len(scripts) > 1 else 0.0
    cyrillic_detected = 1.0 if "Cyrillic" in scripts else 0.0
    greek_detected = 1.0 if "Greek" in scripts else 0.0

    # Normalization check
    nfc = unicodedata.normalize('NFC', decoded_target)
    nfd = unicodedata.normalize('NFD', decoded_target)
    normalization_discrepancy = 1.0 if len(nfc) != len(nfd) else 0.0

    return {
        "is_punycode": is_punycode,
        "mixed_script": mixed_script,
        "confusable_char_count": float(confusable_count),
        "non_ascii_char_count": float(non_ascii_count),
        "cyrillic_detected": cyrillic_detected,
        "greek_detected": greek_detected,
        "unicode_norm_diff": normalization_discrepancy,
    }
