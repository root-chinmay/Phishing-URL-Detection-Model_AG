"""
Standard Unified Inference Engine for MobiURL-Guard.
Executes the full defensive pipeline:
1. URL Preprocessing & Feature Extraction
2. Model Probability Estimation
3. Probability Calibration (Platt / Isotonic)
4. Split Conformal Prediction (Legitimate / Malicious / Uncertain)
5. Out-of-Distribution (OOD) Evaluation
6. Local Explainable AI (XAI) Attribution
7. Optional Message Context Integration
8. Produces validated standard JSON response.
"""

import os
from typing import Dict, Any, Optional, List

from src.features.url_features import URLFeatureExtractor
from src.features.message_features import MessageContextScorer
from src.calibration.probability_calibration import CalibratedProbabilityEstimator
from src.uncertainty.conformal import ConformalPredictor
from src.uncertainty.out_of_distribution import OutOfDistributionDetector
from src.explainability.local_explainer import LocalExplainer
from src.distillation.student import CompactEnsembleStudent


class MobiURLInferenceEngine:
    """
    Production-grade inference pipeline usable on both desktop and mobile Android.
    Can run completely offline.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        brand_config_path: Optional[str] = None,
        alpha: float = 0.05
    ):
        self.feature_extractor = URLFeatureExtractor(brand_config_path)
        self.message_scorer = MessageContextScorer()
        self.calibrator = CalibratedProbabilityEstimator()
        self.conformal_predictor = ConformalPredictor(alpha=alpha)
        self.ood_detector = OutOfDistributionDetector()
        self.explainer = LocalExplainer()
        self.model_version = "1.0.0"

        # Load compact student model if exists
        self.student_model = None
        if model_path and os.path.exists(model_path):
            self.student_model = CompactEnsembleStudent.load_json(model_path)
            self._load_calibration_manifest()
        else:
            # Fallback heuristic rule/tree model if no checkpoint loaded yet
            self._init_default_rule_trees()

    def _load_calibration_manifest(self):
        """Load fitted Platt scaler and conformal q_hat if manifest exists."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        manifest_path = os.path.join(base_dir, "models", "manifests", "calibration_manifest.json")
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join("models", "manifests", "calibration_manifest.json")
        if os.path.exists(manifest_path):
            try:
                import json
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ps = data.get("platt_scaler", {})
                if ps.get("is_fitted"):
                    self.calibrator.scaler.A = ps.get("A", -1.0)
                    self.calibrator.scaler.B = ps.get("B", 0.0)
                    self.calibrator.scaler.is_fitted = True

                conf = data.get("conformal", {})
                self.conformal_predictor.q_hat = conf.get("selected_q_hat", 0.3169)
                self.conformal_predictor.is_calibrated = True
            except Exception:
                pass

    def _init_default_rule_trees(self):
        """Create baseline calibrated heuristic trees so engine functions immediately."""
        from src.distillation.student import CompactTreeNode
        # Tree 1: IP address or Punycode or Brand spoofing
        t1 = CompactTreeNode(
            feature_name="is_ip",
            threshold=0.5,
            left=CompactTreeNode(
                feature_name="is_impersonation_suspected",
                threshold=0.5,
                left=CompactTreeNode(value=0.15),
                right=CompactTreeNode(value=0.88)
            ),
            right=CompactTreeNode(value=0.95)
        )
        # Tree 2: Phishing keywords, shortener, and suspicious TLD
        t2 = CompactTreeNode(
            feature_name="keyword_hits",
            threshold=0.5,
            left=CompactTreeNode(
                feature_name="is_shortener",
                threshold=0.5,
                left=CompactTreeNode(value=0.10),
                right=CompactTreeNode(value=0.72)
            ),
            right=CompactTreeNode(
                feature_name="is_https",
                threshold=0.5,
                left=CompactTreeNode(value=0.92),
                right=CompactTreeNode(value=0.78)
            )
        )
        # Tree 3: Entropy and nested subdomains
        t3 = CompactTreeNode(
            feature_name="entropy",
            threshold=4.2,
            left=CompactTreeNode(
                feature_name="subdom_cnt",
                threshold=2.5,
                left=CompactTreeNode(value=0.12),
                right=CompactTreeNode(value=0.65)
            ),
            right=CompactTreeNode(
                feature_name="confusable_char_count",
                threshold=0.5,
                left=CompactTreeNode(value=0.70),
                right=CompactTreeNode(value=0.96)
            )
        )
        self.student_model = CompactEnsembleStudent(trees=[t1, t2, t3], weights=[0.4, 0.35, 0.25])
        self.conformal_predictor.q_hat = 0.35  # Nominal calibrated threshold
        self.conformal_predictor.is_calibrated = True

    def predict(
        self,
        url: str,
        message_text: Optional[str] = None,
        sender: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute prediction pipeline for a single URL and optional message context.
        """
        clean_url = str(url).strip()
        features = self.feature_extractor.extract_features(clean_url)

        # 1. Base model prediction
        raw_prob = self.student_model.predict_proba(features)

        # 2. Probability calibration
        cal_risk = self.calibrator.predict_risk(raw_prob)
        mal_prob = cal_risk["malicious_probability"]
        benign_prob = cal_risk["benign_probability"]
        risk_pct = cal_risk["risk_percentage"]

        # 3. Conformal Prediction Set
        pred_set, uncertainty_status = self.conformal_predictor.predict_set(mal_prob)

        # 4. Out-of-Distribution Check
        ood_res = self.ood_detector.evaluate(features)

        # 5. Local XAI Attribution
        explanation = self.explainer.explain_instance(features, top_k=4)

        # 6. Optional Message Context Integration
        msg_res = self.message_scorer.analyze(message_text, sender, channel)
        modalities = ["url"]
        if msg_res["message_context_available"] > 0:
            modalities.append("message_context")
            # If high social engineering cues present, adjust risk upwards
            if msg_res["composite_social_engineering_score"] > 0.4:
                risk_pct = min(100.0, risk_pct + (msg_res["composite_social_engineering_score"] * 25.0))
                mal_prob = round(risk_pct / 100.0, 4)
                benign_prob = round(1.0 - mal_prob, 4)
                explanation["human_readable_reasons"].insert(
                    0, f"Social Engineering Cues: {', '.join(msg_res['detected_cues'])}"
                )

        # 7. Final Classification Decision
        # If conformal set is {Legitimate, Malicious}, decision is UNCERTAIN
        if len(pred_set) == 2 or ood_res["is_out_of_distribution"]:
            classification = "uncertain"
            confidence = "low"
        elif "Malicious" in pred_set or risk_pct >= 60.0:
            classification = "malicious"
            confidence = "high" if (risk_pct >= 80.0 or risk_pct <= 20.0) else "medium"
        else:
            classification = "legitimate"
            confidence = "high" if risk_pct <= 20.0 else "medium"

        # Format standard output payload
        return {
            "url": clean_url,
            "classification": classification,
            "malicious_probability": mal_prob,
            "benign_probability": benign_prob,
            "risk_percentage": risk_pct,
            "prediction_confidence": confidence,
            "conformal_prediction_set": [p.lower() for p in pred_set],
            "uncertainty_status": uncertainty_status,
            "out_of_distribution": ood_res["is_out_of_distribution"],
            "available_modalities": modalities,
            "top_reasons": explanation["human_readable_reasons"],
            "features_summary": {
                "length": features["url_len"],
                "domain": features["dom_len"],
                "is_https": bool(features["is_https"]),
                "entropy": features["entropy"],
                "is_ip": bool(features["is_ip"]),
                "is_shortener": bool(features["is_shortener"]),
                "brand_score": features["brand_impersonation_score"]
            },
            "model_version": self.model_version
        }
