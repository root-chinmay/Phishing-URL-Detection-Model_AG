"""
Local Storage and Opt-In Scan History Manager for MobiURL-Guard.
Privacy-First Architecture:
- History is opt-in (disabled by default)
- Storage resides strictly locally on the user's mobile device
- User can search, filter, or clear all historical scan records at any time.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional


class LocalScanStorage:
    def __init__(self, storage_dir: str = "models/manifests"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.settings_file = os.path.join(self.storage_dir, "app_settings.json")
        self.history_file = os.path.join(self.storage_dir, "scan_history.json")
        self._init_defaults()

    def _init_defaults(self):
        if not os.path.exists(self.settings_file):
            default_settings = {
                "opt_in_history": False,
                "offline_mode": True,
                "conformal_alpha": 0.05,
                "allow_network_redirect": False,
                "model_version": "1.0.0",
                "app_version": "1.0.0"
            }
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, indent=2)

        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_settings(self) -> Dict[str, Any]:
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"opt_in_history": False, "offline_mode": True}

    def update_settings(self, new_settings: Dict[str, Any]):
        curr = self.get_settings()
        curr.update(new_settings)
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(curr, f, indent=2)

    def is_history_enabled(self) -> bool:
        return self.get_settings().get("opt_in_history", False)

    def save_scan_result(self, result: Dict[str, Any]):
        """Save a scan result if opt-in history is active."""
        if not self.is_history_enabled():
            return

        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": result.get("url"),
            "classification": result.get("classification"),
            "risk_percentage": result.get("risk_percentage"),
            "prediction_confidence": result.get("prediction_confidence"),
            "conformal_prediction_set": result.get("conformal_prediction_set"),
            "top_reasons": result.get("top_reasons", [])[:2]
        }

        history = self.get_history()
        history.insert(0, record)
        # Keep maximum 100 recent scans
        history = history[:100]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def get_history(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                records = json.load(f)
            if filter_query:
                q = filter_query.lower()
                records = [r for r in records if q in r.get("url", "").lower() or q in r.get("classification", "").lower()]
            return records
        except Exception:
            return []

    def clear_history(self):
        """Wipe all scan history records."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump([], f)
