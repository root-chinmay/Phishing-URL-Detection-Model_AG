"""
Cybersecurity Design Theme and Design Tokens for MobiURL-Guard.
Professional dark-mode cybersecurity palette with semantic risk indicators:
- High Risk / Malicious: Crimson Red (#E63946 / [0.90, 0.22, 0.27, 1.0])
- Medium Risk / Suspicious: Amber (#F4A261 / [0.95, 0.63, 0.38, 1.0])
- Low Risk / Safe: Emerald Green (#2A9D8F / [0.16, 0.61, 0.56, 1.0])
- Uncertain / Info: Cyan (#00B4D8 / [0.0, 0.70, 0.84, 1.0])
- Background: Deep Navy (#0B132B / [0.04, 0.07, 0.17, 1.0])
- Card Surface: Slate Navy (#1C2541 / [0.11, 0.14, 0.25, 1.0])
"""

class ThemeColors:
    # RGBA values (0.0 to 1.0 range used by Kivy)
    PRIMARY = [0.0, 0.70, 0.84, 1.0]      # Electric Cyan
    PRIMARY_DARK = [0.02, 0.40, 0.55, 1.0]
    SECONDARY = [0.16, 0.61, 0.56, 1.0]    # Emerald
    BACKGROUND = [0.04, 0.07, 0.17, 1.0]   # Deep Navy
    SURFACE = [0.11, 0.14, 0.25, 1.0]      # Card Slate
    SURFACE_LIGHT = [0.18, 0.23, 0.38, 1.0]
    TEXT_PRIMARY = [0.95, 0.96, 0.98, 1.0] # White
    TEXT_SECONDARY = [0.65, 0.70, 0.80, 1.0] # Muted
    
    # Semantic status colors
    SAFE = [0.16, 0.61, 0.56, 1.0]         # Green
    SUSPICIOUS = [0.95, 0.63, 0.38, 1.0]   # Amber
    MALICIOUS = [0.90, 0.22, 0.27, 1.0]    # Crimson Red
    UNCERTAIN = [0.0, 0.70, 0.84, 1.0]     # Cyan


def get_risk_color(risk_percentage: float) -> list:
    """Return RGBA color corresponding to calibrated risk score."""
    if risk_percentage >= 70.0:
        return ThemeColors.MALICIOUS
    elif risk_percentage >= 40.0:
        return ThemeColors.SUSPICIOUS
    else:
        return ThemeColors.SAFE
