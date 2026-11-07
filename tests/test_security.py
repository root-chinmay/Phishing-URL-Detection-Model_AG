"""Unit tests for defensive cybersecurity controls & SSRF prevention."""

import pytest
from src.security.redirect_analysis import is_safe_public_ip, RedirectAnalyzer


def test_ssrf_ip_filtering():
    # Loopback
    assert is_safe_public_ip("127.0.0.1") is False
    assert is_safe_public_ip("::1") is False

    # Private RFC1918
    assert is_safe_public_ip("192.168.1.1") is False
    assert is_safe_public_ip("10.0.0.5") is False
    assert is_safe_public_ip("172.16.0.1") is False

    # Link-local / Cloud metadata IP (AWS/GCP/Azure)
    assert is_safe_public_ip("169.254.169.254") is False

    # Public IP
    assert is_safe_public_ip("8.8.8.8") is True
    assert is_safe_public_ip("1.1.1.1") is True


def test_offline_redirect_analyzer():
    analyzer = RedirectAnalyzer(allow_network_resolution=False)
    res = analyzer.resolve_chain_safely("https://bit.ly/test-link")
    assert res["network_resolution_enabled"] is False
    assert res["hop_count"] == 0
