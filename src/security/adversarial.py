"""
Adversarial URL Generation and Robustness Evaluation Engine for MobiURL-Guard (Research Gap 4).
Applies controlled, synthetic evasion transformations to URLs:
1. Homoglyph substitution (Cyrillic / Greek lookalikes)
2. Typosquatting (omission, transposition, duplicate keystroke, bit-flip)
3. Subdomain injection (impersonation prefix on test domains)
4. URL padding & entropy inflation
5. Percent / Hex encoding obfuscation
6. Parameter manipulation & nested redirects
7. Case transformations

All synthetic domain tests use reserved '.test' domains (RFC 2606).
"""

import random
import re
from urllib.parse import urlparse, urlunparse, quote
from typing import Dict, List, Any, Optional

# Cyrillic confusables for common Latin characters
HOMOGLYPH_MAP = {
    'a': '\u0430',  # cyrillic small a
    'c': '\u0441',  # cyrillic small es
    'e': '\u0435',  # cyrillic small ie
    'i': '\u0456',  # cyrillic small byelorussian-ukrainian i
    'j': '\u0458',  # cyrillic small je
    'o': '\u043e',  # cyrillic small o
    'p': '\u0440',  # cyrillic small er
    's': '\u0455',  # cyrillic small dze
    'x': '\u0445',  # cyrillic small ha
    'y': '\u0443',  # cyrillic small u
}


class AdversarialURLEngine:
    """
    Generates controlled adversarial variants of URLs to test detector robustness.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def apply_homoglyphs(self, url: str) -> str:
        """Substitute random Latin characters with visually identical Cyrillic lookalikes."""
        chars = list(url)
        substituted = False
        for i, c in enumerate(chars):
            lower = c.lower()
            if lower in HOMOGLYPH_MAP and self.rng.random() < 0.4:
                chars[i] = HOMOGLYPH_MAP[lower]
                substituted = True
        if not substituted:
            # Force at least one replacement if possible
            for i, c in enumerate(chars):
                if c.lower() in HOMOGLYPH_MAP:
                    chars[i] = HOMOGLYPH_MAP[c.lower()]
                    break
        return "".join(chars)

    def apply_typosquatting(self, url: str) -> str:
        """Introduce character omission, swap, or insertion in domain."""
        parsed = urlparse(url if "://" in url else f"http://{url}")
        host = parsed.netloc or parsed.path
        if "." in host:
            parts = host.split(".")
            domain_label = list(parts[0])
            if len(domain_label) > 3:
                action = self.rng.choice(["omit", "swap", "duplicate"])
                idx = self.rng.randint(1, len(domain_label) - 2)
                if action == "omit":
                    domain_label.pop(idx)
                elif action == "swap":
                    domain_label[idx], domain_label[idx+1] = domain_label[idx+1], domain_label[idx]
                elif action == "duplicate":
                    domain_label.insert(idx, domain_label[idx])
                parts[0] = "".join(domain_label)
                new_netloc = ".".join(parts)
                return urlunparse((parsed.scheme, new_netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        return url + "-security-check.test"

    def apply_subdomain_injection(self, url: str, brand: str = "login-service") -> str:
        """Inject target brand/action as a subdomain on a test domain."""
        parsed = urlparse(url if "://" in url else f"http://{url}")
        new_netloc = f"{brand}.verify-gateway.test"
        return urlunparse((parsed.scheme or "https", new_netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    def apply_url_padding(self, url: str, padding_length: int = 80) -> str:
        """Append long benign-looking hex or alphanumeric query padding to distort length and entropy."""
        padding = "".join(self.rng.choices("abcdef0123456789", k=padding_length))
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}token_verification_digest={padding}"

    def apply_percent_encoding(self, url: str) -> str:
        """Hex-encode standard characters in the path to evade naive pattern matching."""
        parsed = urlparse(url if "://" in url else f"http://{url}")
        path = parsed.path
        if path:
            encoded_path = "".join(f"%{ord(c):02X}" if self.rng.random() < 0.5 and c not in "/" else c for c in path)
        else:
            encoded_path = "/%76%65%72%69%66%79"
        return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

    def apply_nested_redirect(self, url: str) -> str:
        """Wrap target destination inside an open redirect parameter."""
        encoded_dest = quote(url, safe="")
        return f"https://gateway.secure-auth.test/redirect?dest={encoded_dest}&source=oauth2"

    def apply_case_randomization(self, url: str) -> str:
        """Randomize uppercase and lowercase letters in path and query."""
        parsed = urlparse(url if "://" in url else f"http://{url}")
        path_query = parsed.path + ("?" + parsed.query if parsed.query else "")
        randomized = "".join(c.upper() if self.rng.random() < 0.5 else c.lower() for c in path_query)
        return urlunparse((parsed.scheme, parsed.netloc, randomized, "", "", ""))

    def generate_adversarial_suite(self, base_url: str) -> Dict[str, str]:
        """
        Generate a complete suite of evasive adversarial variants for a given URL.
        """
        return {
            "clean": base_url,
            "homoglyph": self.apply_homoglyphs(base_url),
            "typosquat": self.apply_typosquatting(base_url),
            "subdomain_injected": self.apply_subdomain_injection(base_url),
            "padded": self.apply_url_padding(base_url),
            "percent_encoded": self.apply_percent_encoding(base_url),
            "nested_redirect": self.apply_nested_redirect(base_url),
            "case_randomized": self.apply_case_randomization(base_url),
        }
