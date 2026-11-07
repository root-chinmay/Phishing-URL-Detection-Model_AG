"""
Data Preprocessing Pipeline for MobiURL-Guard.
Extracts and converts feature dictionaries into numerical feature arrays.
Handles numerical type conversion, missing value imputation, and label extraction.
"""

from typing import List, Dict, Any, Tuple, Optional
from src.features.url_features import URLFeatureExtractor


class DataPreprocessor:
    def __init__(self, feature_names: Optional[List[str]] = None):
        self.extractor = URLFeatureExtractor()
        self.feature_names = feature_names or self.extractor.get_base_feature_names()

    def process_records(
        self,
        records: List[Dict[str, Any]],
        label_col: str = "label",
        url_col: str = "url",
        extract_from_raw_url: bool = False
    ) -> Tuple[List[List[float]], List[int], List[str]]:
        """
        Converts records to (X_matrix, y_vector, urls).
        If extract_from_raw_url is True, recalculates all features via the feature extractor.
        Otherwise, uses pre-extracted features present in the dataset columns.
        """
        X = []
        y = []
        urls = []

        for r in records:
            u = r.get(url_col, "")
            lbl = int(float(r.get(label_col, 0)))

            if extract_from_raw_url:
                feat_dict = self.extractor.extract_features(u)
                row = [feat_dict.get(fn, 0.0) for fn in self.feature_names]
            else:
                row = []
                for fn in self.feature_names:
                    raw_val = r.get(fn, 0.0)
                    try:
                        val = float(raw_val)
                    except (ValueError, TypeError):
                        val = 0.0
                    row.append(val)

            X.append(row)
            y.append(lbl)
            urls.append(u)

        return X, y, urls
