"""
Data Validation and Quality Assurance for MobiURL-Guard.
Validates URL formatting, label values, and detects corrupted rows.
"""

from typing import Dict, List, Any, Tuple


class DataValidator:
    """Validates records before training or feature extraction."""

    @staticmethod
    def validate_record(record: Dict[str, Any], url_col: str = "url", label_col: str = "label") -> bool:
        """Check if record contains valid non-empty URL and integer label."""
        url = record.get(url_col)
        if not url or not isinstance(url, str) or len(url.strip()) == 0:
            return False

        label = record.get(label_col)
        if label is None:
            return False

        try:
            int_lbl = int(float(label))
            if int_lbl not in (0, 1):
                return False
        except (ValueError, TypeError):
            return False

        return True

    @classmethod
    def filter_clean_records(
        cls,
        records: List[Dict[str, Any]],
        url_col: str = "url",
        label_col: str = "label"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Filters valid records and returns count of rejected rows."""
        clean = []
        rejected = 0
        for r in records:
            if cls.validate_record(r, url_col, label_col):
                clean.append(r)
            else:
                rejected += 1
        return clean, rejected
