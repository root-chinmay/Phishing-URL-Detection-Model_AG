"""Unit tests for adversarial perturbation suite."""

import pytest
from src.security.adversarial import AdversarialURLEngine


def test_adversarial_transformations():
    engine = AdversarialURLEngine(seed=42)
    base_url = "https://paypal-service.test/verify"
    suite = engine.generate_adversarial_suite(base_url)

    assert "homoglyph" in suite
    assert "typosquat" in suite
    assert "subdomain_injected" in suite
    assert "padded" in suite
    assert "percent_encoded" in suite
    assert "nested_redirect" in suite

    # Ensure padding changed length
    assert len(suite["padded"]) > len(base_url)
    # Ensure percent encoding added percent symbols
    assert "%" in suite["percent_encoded"]
