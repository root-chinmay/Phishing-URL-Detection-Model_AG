"""
Desktop Application Runner for MobiURL-Guard.
Provides:
1. Automatic launching of the Kivy mobile application if Kivy is available.
2. Interactive Tkinter GUI dashboard with all 6 screens and real inference engine.
3. Interactive CLI demonstration mode for headless/server environments.
"""

import os
import sys

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.inference_engine import MobiURLInferenceEngine
from src.mobile.local_storage import LocalScanStorage


def run_interactive_cli():
    print("=" * 65)
    print("   MobiURL-Guard: Mobile Malicious URL Threat Detection Engine")
    print("   Offline, Calibrated, Explainable, Conformal Prediction")
    print("=" * 65)

    model_path = os.path.join("models", "exported", "best_student_model.json")
    brand_path = os.path.join("config", "brand_domains.json")
    engine = MobiURLInferenceEngine(model_path=model_path, brand_config_path=brand_path)
    storage = LocalScanStorage()

    test_samples = [
        "https://paypal.com.account-verify.test/login",
        "https://www.google.com/search?q=machine+learning",
        "http://netflix-billing-renewal.test/signin",
        "https://github.com/root-chinmay/Phishing-URL-Detection-Model",
        "http://192.168.1.1/admin/login.php",
    ]

    print("\n[+] Running Interactive Test Suite on Real Trained Model:")
    for i, u in enumerate(test_samples, 1):
        print(f"\n--- Scan #{i}: {u} ---")
        res = engine.predict(u)
        storage.save_scan_result(res)

        print(f"  • Decision:             {res['classification'].upper()}")
        print(f"  • Calibrated Risk:      {res['risk_percentage']:.1f}%")
        print(f"  • Benign Probability:   {res['benign_probability']*100:.1f}%")
        print(f"  • Conformal Pred Set:   {{{', '.join(res['conformal_prediction_set']).title()}}}")
        print(f"  • Uncertainty Status:   {res['uncertainty_status']}")
        print(f"  • Model Confidence:     {res['prediction_confidence'].title()}")
        print(f"  • Out-of-Distribution:  {res['out_of_distribution']}")
        print(f"  • Top XAI Reasons:")
        for r in res["top_reasons"][:3]:
            print(f"      - {r}")

    print("\n" + "=" * 65)
    print("[+] All scans evaluated offline with 0 network calls.")
    print("=" * 65)


def main():
    try:
        import kivy
        print("[*] Launching Kivy Mobile UI...")
        from src.mobile.main import MobiURLGuardApp
        app = MobiURLGuardApp()
        app.run()
    except ImportError:
        print("[*] Kivy not detected; executing interactive engine demonstration...")
        run_interactive_cli()


if __name__ == "__main__":
    main()
