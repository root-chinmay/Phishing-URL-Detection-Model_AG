"""Unit tests for URL feature extraction."""

import pytest
from src.features.url_features import URLFeatureExtractor


def test_url_feature_extraction_keys():
    extractor = URLFeatureExtractor()
    url = "https://paypal.com.account-verify.test/login?token=abc"
    feats = extractor.extract_features(url)

    expected_base_keys = [
        "url_len", "dom_len", "is_ip", "tld_len", "subdom_cnt", "letter_cnt",
        "digit_cnt", "special_cnt", "eq_cnt", "qm_cnt", "amp_cnt", "dot_cnt",
        "dash_cnt", "under_cnt", "letter_ratio", "digit_ratio", "spec_ratio",
        "is_https", "slash_cnt", "entropy", "path_len", "query_len"
    ]

    for k in expected_base_keys:
        assert k in feats, f"Missing expected key: {k}"
        assert isinstance(feats[k], (int, float)), f"Key {k} is not numeric"


def test_https_detection():
    extractor = URLFeatureExtractor()
    assert extractor.extract_features("https://secure.test")["is_https"] == 1.0
    assert extractor.extract_features("http://insecure.test")["is_https"] == 0.0


def test_ip_detection():
    extractor = URLFeatureExtractor()
    assert extractor.extract_features("http://192.168.1.1/login")["is_ip"] == 1.0
    assert extractor.extract_features("https://google.com/search")["is_ip"] == 0.0
