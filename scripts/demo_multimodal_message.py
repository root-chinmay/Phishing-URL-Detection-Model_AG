"""
Multimodal Message Context Demonstration Script for MobiURL-Guard (Research Gap 6).
Evaluates social engineering cues in accompanying SMS / WhatsApp text:
- Urgency indicators
- Threatening language (suspension, legal action)
- Reward / prize lures
- Credential / OTP solicitation
- Combines message risk score with URL feature evaluation.
"""

import os
import sys

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.inference_engine import MobiURLInferenceEngine


def run_multimodal_demo():
    print("=" * 65)
    print("   MobiURL-Guard: Multimodal Message-Context Threat Scoring")
    print("=" * 65)

    engine = MobiURLInferenceEngine()

    test_scenarios = [
        {
            "channel": "SMS",
            "sender": "+1-800-CHASE-ALERT",
            "message": "URGENT: Your Chase checking account has been temporarily suspended due to unauthorized login attempts. Click immediately to verify your identity or your debit card will be blocked: https://chase-bank-alert-resolution.test/auth",
            "url": "https://chase-bank-alert-resolution.test/auth"
        },
        {
            "channel": "WhatsApp",
            "sender": "DHL Express Tracking",
            "message": "Your package cannot be delivered due to unpaid customs fee of $2.40. Tap link right now to pay: http://dhl-express-tracking-package.test/deliver",
            "url": "http://dhl-express-tracking-package.test/deliver"
        },
        {
            "channel": "Email / Chat",
            "sender": "Colleague",
            "message": "Hey Chinmay, here is the official research paper documentation for review: https://www.python.org/downloads/",
            "url": "https://www.python.org/downloads/"
        }
    ]

    for i, s in enumerate(test_scenarios, 1):
        print(f"\n--- Scenario #{i} [{s['channel']}] From: {s['sender']} ---")
        print(f"Message Body: \"{s['message']}\"")
        res = engine.predict(url=s["url"], message_text=s["message"], sender=s["sender"], channel=s["channel"])

        print(f"  • Decision:             {res['classification'].upper()}")
        print(f"  • Calibrated Risk:      {res['risk_percentage']:.1f}%")
        print(f"  • Conformal Pred Set:   {{{', '.join(res['conformal_prediction_set']).title()}}}")
        print(f"  • Modalities Used:      {', '.join(res['available_modalities'])}")
        print(f"  • Top Explanatory Cues:")
        for r in res["top_reasons"][:3]:
            print(f"      - {r}")

    print("\n" + "=" * 65)
    print("[+] Multimodal message scoring completed purely on-device.")
    print("=" * 65)


if __name__ == "__main__":
    run_multimodal_demo()
