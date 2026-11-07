"""Unit tests for desktop versus mobile model consistency."""

import os
import pytest
from src.distillation.student import CompactTreeNode, CompactEnsembleStudent
from src.models.inference_engine import MobiURLInferenceEngine


def test_compact_student_serialization(tmp_path):
    t1 = CompactTreeNode(
        feature_name="url_len",
        threshold=50.0,
        left=CompactTreeNode(value=0.1),
        right=CompactTreeNode(value=0.9)
    )
    student = CompactEnsembleStudent(trees=[t1], feature_names=["url_len"])
    export_file = str(tmp_path / "test_model.json")
    student.save_json(export_file)

    loaded = CompactEnsembleStudent.load_json(export_file)
    assert len(loaded.trees) == 1
    assert loaded.trees[0].threshold == 50.0

    # Test bit-identical predictions
    feat_short = {"url_len": 30.0}
    feat_long = {"url_len": 70.0}
    assert student.predict_proba(feat_short) == loaded.predict_proba(feat_short) == 0.1
    assert student.predict_proba(feat_long) == loaded.predict_proba(feat_long) == 0.9
