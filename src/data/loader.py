"""
Configurable Dataset Ingestion Module for MobiURL-Guard.
Reads dataset configuration from config/dataset_config.yaml,
validates columns, and loads data into structured dictionary or tabular records.
"""

import os
import csv
import yaml
from typing import Dict, List, Any, Tuple, Optional


class DatasetLoader:
    def __init__(self, config_path: str = "config/dataset_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {
            "dataset": {
                "raw_path": "data/raw/dataset.csv",
                "url_column": "url",
                "label_column": "label",
                "domain_column": "dom",
                "positive_class": 1,
                "negative_class": 0
            }
        }

    def load_raw_records(self, path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Loads CSV dataset as a list of row dictionaries using standard library.
        Returns (records, header_columns).
        """
        target_path = path or self.config["dataset"]["raw_path"]
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Dataset file not found at: {target_path}")

        records = []
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            for row in reader:
                records.append(row)

        return records, headers
