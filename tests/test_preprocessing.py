"""Unit tests for dataset loader, validator, and preprocessor."""

import pytest
from src.data.validation import DataValidator
from src.data.preprocessing import DataPreprocessor
from src.data.splitting import DataSplitter, canonicalize_url_str


def test_validator():
    valid_record = {"url": "https://example.com", "label": "1"}
    assert DataValidator.validate_record(valid_record) is True

    invalid_url = {"url": "", "label": "0"}
    assert DataValidator.validate_record(invalid_url) is False

    invalid_label = {"url": "https://example.com", "label": "unknown"}
    assert DataValidator.validate_record(invalid_label) is False


def test_canonicalize_url():
    u1 = "https://www.Example.com/path/"
    u2 = "http://example.com/path"
    assert canonicalize_url_str(u1) == canonicalize_url_str(u2)


def test_splitter_deduplication():
    records = [
        {"url": "https://example.com/", "label": 0},
        {"url": "http://www.example.com", "label": 0},
        {"url": "https://unique.test", "label": 1},
    ]
    splitter = DataSplitter()
    deduped = splitter.deduplicate(records)
    assert len(deduped) == 2
