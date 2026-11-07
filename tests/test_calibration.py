"""Unit tests for probability calibration and metrics."""

import pytest
from src.calibration.probability_calibration import (
    PlattScaler,
    CalibratedProbabilityEstimator,
    compute_ece_and_bins,
    compute_brier_score
)


def test_platt_scaler():
    scaler = PlattScaler()
    scores = [0.1, 0.2, 0.8, 0.9, 0.85]
    labels = [0, 0, 1, 1, 1]
    scaler.fit(scores, labels, epochs=50)
    assert scaler.is_fitted is True

    cal_low = scaler.calibrate(0.1)
    cal_high = scaler.calibrate(0.9)
    assert cal_low < cal_high
    assert 0.0 <= cal_low <= 1.0


def test_ece_computation():
    probs = [0.1, 0.2, 0.8, 0.9]
    labels = [0, 0, 1, 1]
    res = compute_ece_and_bins(probs, labels, n_bins=5)
    assert "ece" in res
    assert "mce" in res
    assert 0.0 <= res["ece"] <= 1.0


def test_brier_score():
    probs = [1.0, 0.0]
    labels = [1, 0]
    assert compute_brier_score(probs, labels) == 0.0
