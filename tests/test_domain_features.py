"""Unit tests for domain and structure features."""

import pytest
from src.features.domain_features import extract_domain_features, is_ip_address, parse_domain_structure


def test_ip_address_checker():
    assert is_ip_address("192.168.1.1") is True
    assert is_ip_address("10.0.0.1:8080") is True
    assert is_ip_address("google.com") is False
    assert is_ip_address("") is False


def test_domain_structure_parsing():
    sub, reg, tld = parse_domain_structure("verify.accounts.google.com")
    assert reg == "google.com"
    assert tld == "com"
    assert sub == "verify.accounts"


def test_shortener_detection():
    feats = extract_domain_features("https://bit.ly/3xY8a", hostname="bit.ly")
    assert feats["is_shortener"] == 1.0

    feats_normal = extract_domain_features("https://google.com", hostname="google.com")
    assert feats_normal["is_shortener"] == 0.0
