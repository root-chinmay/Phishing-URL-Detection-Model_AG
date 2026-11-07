"""Unit tests for inference engine and risk predictions."""

import pytest
from src.models.inference_engine import MobiURLInferenceEngine


def test_inference_engine_output_schema():
    engine = MobiURLInferenceEngine()
    result = engine.predict("https://paypal.com.account-verify.test/login")

    required_keys = [
        "url", "classification", "malicious_probability", "benign_probability",
        "risk_percentage", "prediction_confidence", "conformal_prediction_set",
        "uncertainty_status", "out_of_distribution", "available_modalities",
        "top_reasons", "model_version"
    ]

    for k in required_keys:
        assert k in result, f"Result missing key: {k}"

    assert 0.0 <= result["risk_percentage"] <= 100.0
    assert 0.0 <= result["malicious_probability"] <= 1.0
    assert 0.0 <= result["benign_probability"] <= 1.0
    assert abs((result["malicious_probability"] + result["benign_probability"]) - 1.0) < 0.05
    assert result["classification"] in ["legitimate", "malicious", "uncertain"]
    assert isinstance(result["conformal_prediction_set"], list)
    assert len(result["top_reasons"]) > 0
