"""
MobiURL-Guard: Android Mobile Application Main Entrypoint.
Built with Python and Kivy for native on-device execution.
"""

import os
import sys

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.mobile.theme import ThemeColors
from src.mobile.local_storage import LocalScanStorage
from src.models.inference_engine import MobiURLInferenceEngine
from src.mobile.screens import (
    HomeScreen,
    AnalysisScreen,
    RiskAssessmentScreen,
    DetailedAnalysisScreen,
    ScanHistoryScreen,
    SettingsScreen,
    KIVY_AVAILABLE
)

if KIVY_AVAILABLE:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, SlideTransition
    from kivy.core.window import Window

    # Configure mobile viewport aspect ratio for desktop emulation
    Window.size = (380, 680)
    Window.clearcolor = ThemeColors.BACKGROUND

    class MobiURLGuardApp(App):
        def build(self):
            self.title = "MobiURL-Guard"
            self.icon = os.path.join("assets", "icons", "icon.png")

            # Initialize Core Engines
            model_path = os.path.join("models", "exported", "best_student_model.json")
            brand_path = os.path.join("config", "brand_domains.json")
            self.engine = MobiURLInferenceEngine(model_path=model_path, brand_config_path=brand_path)
            self.storage = LocalScanStorage()

            # Initialize Screen Manager with Smooth Transition
            sm = ScreenManager(transition=SlideTransition(duration=0.2))
            sm.add_widget(HomeScreen(engine=self.engine, storage=self.storage, name="home"))
            sm.add_widget(AnalysisScreen(engine=self.engine, storage=self.storage, name="analysis"))
            sm.add_widget(RiskAssessmentScreen(name="risk"))
            sm.add_widget(DetailedAnalysisScreen(name="details"))
            sm.add_widget(ScanHistoryScreen(storage=self.storage, name="history"))
            sm.add_widget(SettingsScreen(storage=self.storage, name="settings"))

            return sm

else:
    class MobiURLGuardApp:
        def run(self):
            print("[!] Kivy is not installed in the current environment.")
            print("[*] To launch the interactive desktop interface, run: python scripts/run_desktop_app.py")


if __name__ == "__main__":
    app = MobiURLGuardApp()
    app.run()
