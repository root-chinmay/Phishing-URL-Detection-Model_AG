"""Unit tests for split conformal prediction."""

import pytest
from src.uncertainty.conformal import ConformalPredictor


def test_conformal_calibration():
    cp = ConformalPredictor(alpha=0.05)
    cal_probs = [0.05] * 50 + [0.95] * 50
    cal_labels = [0] * 50 + [1] * 50

    q_hat = cp.fit_calibration(cal_probs, cal_labels)
    assert cp.is_calibrated is True
    assert 0.0 <= q_hat <= 1.0


def test_conformal_prediction_set():
    cp = ConformalPredictor(alpha=0.05)
    cp.q_hat = 0.20
    cp.is_calibrated = True

    # High probability malicious
    pred_mal, status_mal = cp.predict_set(0.95)
    assert "Malicious" in pred_mal
    assert len(pred_mal) == 1

    # Borderline ambiguous probability with broad quantile -> Uncertain set {Legitimate, Malicious}
    cp.q_hat = 0.65
    pred_unc, status_unc = cp.predict_set(0.50)
    assert len(pred_unc) == 2
    assert "Legitimate" in pred_unc
    assert "Malicious" in pred_unc
    assert "Uncertain" in status_unc
