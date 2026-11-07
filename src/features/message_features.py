"""
Message Context Analysis Module for MobiURL-Guard (Research Gap 6).
Analyzes user-provided SMS, WhatsApp, or Email message context accompanying a URL.
Extracts:
- Urgency indicators
- Threatening / coercive language
- Reward / lottery / prize hooks
- Account suspension claims
- Credential / OTP / verification requests
- Financial / payment transaction requests
- Call-to-action click pressure
"""

import re
from typing import Dict, Any, Optional

# Keyword and regex patterns for social engineering indicators
URGENCY_PATTERNS = [
    r"\b(urgent|immediately|right now|within \d+ hours?|asap|expires? (today|soon)|act now|time sensitive)\b"
]

THREAT_PATTERNS = [
    r"\b(suspended|deactivated|terminated|closed|locked|arrest(ed)?|law enforcement|legal action|penalty|fine)\b"
]

PRIZE_PATTERNS = [
    r"\b(congratulations|you('ve| have)? won|winner|lottery|free gift|claim (your|now)|cash prize|reward|bonus)\b"
]

CREDENTIAL_PATTERNS = [
    r"\b(password|passcode|pin|security code|verify (your )?identity|update (your )?(details|account)|sign in now)\b"
]

OTP_PATTERNS = [
    r"\b(otp|one[- ]time[- ]password|verification code|auth(entication)? code|2fa|security token)\b"
]

PAYMENT_PATTERNS = [
    r"\b(payment|wire|transfer|refund|invoice|unpaid|due amount|bank account|credit card|bitcoin|crypto|usdt)\b"
]

CTA_PATTERNS = [
    r"\b(click (here|the link|below)|tap (here|link)|follow (this )?link|open link)\b"
]


class MessageContextScorer:
    """
    Evaluates risk score of accompanying messaging context.
    Works purely locally and preserves privacy (no text leaves device).
    """

    def __init__(self):
        self.urgency_re = re.compile("|".join(URGENCY_PATTERNS), re.IGNORECASE)
        self.threat_re = re.compile("|".join(THREAT_PATTERNS), re.IGNORECASE)
        self.prize_re = re.compile("|".join(PRIZE_PATTERNS), re.IGNORECASE)
        self.credential_re = re.compile("|".join(CREDENTIAL_PATTERNS), re.IGNORECASE)
        self.otp_re = re.compile("|".join(OTP_PATTERNS), re.IGNORECASE)
        self.payment_re = re.compile("|".join(PAYMENT_PATTERNS), re.IGNORECASE)
        self.cta_re = re.compile("|".join(CTA_PATTERNS), re.IGNORECASE)

    def analyze(self, text: Optional[str] = None, sender: Optional[str] = None, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze message text and return risk indicators.
        If text is None or empty, returns zeroed features and marks available=False.
        """
        if not text or not text.strip():
            return {
                "message_context_available": 0.0,
                "urgency_score": 0.0,
                "threat_score": 0.0,
                "prize_score": 0.0,
                "credential_request_score": 0.0,
                "otp_request_score": 0.0,
                "payment_score": 0.0,
                "cta_pressure_score": 0.0,
                "composite_social_engineering_score": 0.0,
                "detected_cues": [],
                "validation_status": "No message context provided"
            }

        text_clean = text.strip()
        cues = []

        urgency_matches = len(self.urgency_re.findall(text_clean))
        if urgency_matches > 0:
            cues.append("Urgent / Time-pressure language")

        threat_matches = len(self.threat_re.findall(text_clean))
        if threat_matches > 0:
            cues.append("Threatening / Account suspension threat")

        prize_matches = len(self.prize_re.findall(text_clean))
        if prize_matches > 0:
            cues.append("Reward / Prize lure")

        credential_matches = len(self.credential_re.findall(text_clean))
        if credential_matches > 0:
            cues.append("Credential or password request")

        otp_matches = len(self.otp_re.findall(text_clean))
        if otp_matches > 0:
            cues.append("OTP or 2FA code solicitation")

        payment_matches = len(self.payment_re.findall(text_clean))
        if payment_matches > 0:
            cues.append("Payment / Financial lure")

        cta_matches = len(self.cta_re.findall(text_clean))
        if cta_matches > 0:
            cues.append("Direct click / Action pressure")

        # Composite score in range [0.0, 1.0]
        raw_score = (
            (urgency_matches * 1.5) +
            (threat_matches * 2.0) +
            (prize_matches * 1.8) +
            (credential_matches * 2.5) +
            (otp_matches * 3.0) +
            (payment_matches * 1.5) +
            (cta_matches * 1.2)
        )
        normalized_score = min(1.0, round(raw_score / 10.0, 4))

        return {
            "message_context_available": 1.0,
            "urgency_score": float(urgency_matches),
            "threat_score": float(threat_matches),
            "prize_score": float(prize_matches),
            "credential_request_score": float(credential_matches),
            "otp_request_score": float(otp_matches),
            "payment_score": float(payment_matches),
            "cta_pressure_score": float(cta_matches),
            "composite_social_engineering_score": normalized_score,
            "detected_cues": cues,
            "validation_status": "Unvalidated standalone heuristic (paired training data not provided in dataset)"
        }
