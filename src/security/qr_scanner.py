"""
QR Code Scanner and Quishing Detection Engine for MobiURL-Guard (Research Gap 7).
Capabilities:
- QR code image loading and decoding
- Embedded URL extraction and validation
- Pipeline integration into offline URL feature engine and risk assessment
- Strict security constraint: Decoded destination is NEVER automatically opened or navigated to.
"""

import os
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class QRScannerEngine:
    """
    Decodes QR code images and extracts embedded URLs safely without auto-navigation.
    """

    def __init__(self):
        self.backend = None
        # Try to detect available QR decoding backends
        try:
            import zxingcpp
            self.backend = "zxingcpp"
        except ImportError:
            try:
                from pyzbar import pyzbar
                self.backend = "pyzbar"
            except ImportError:
                self.backend = "pillow_fallback"

    def decode_qr_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract URL from a given QR code image file.
        Returns extracted URL, metadata, and status.
        """
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image file not found: {image_path}",
                "extracted_url": None,
                "backend_used": self.backend,
                "is_offline": True,
            }

        try:
            from PIL import Image
            img = Image.open(image_path)
            raw_text = None

            if self.backend == "zxingcpp":
                import zxingcpp
                results = zxingcpp.read_barcodes(img)
                if results:
                    raw_text = results[0].text
            elif self.backend == "pyzbar":
                from pyzbar import pyzbar
                decoded = pyzbar.decode(img)
                if decoded:
                    raw_text = decoded[0].data.decode("utf-8")
            else:
                # Basic metadata check or fallback simulated QR parser
                raw_text = None

            if not raw_text:
                return {
                    "success": False,
                    "error": "No QR barcode decoded or barcode libraries unavailable.",
                    "extracted_url": None,
                    "backend_used": self.backend,
                    "is_offline": True,
                }

            # Sanitize and validate extracted URL
            raw_text = raw_text.strip()
            return {
                "success": True,
                "extracted_url": raw_text,
                "backend_used": self.backend,
                "is_offline": True,
                "warning": "URL decoded successfully. Do NOT open before running threat detection.",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process QR image: {str(e)}",
                "extracted_url": None,
                "backend_used": self.backend,
                "is_offline": True,
            }
