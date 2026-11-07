"""
Vercel Serverless API Handler for MobiURL-Guard.
Provides RESTful endpoints for online demo and API access:
- POST /api/predict & /predict: Analyzes URL and returns calibrated threat breakdown
- GET /api/health & /health: Health check and model metadata
- Serves interactive cybersecurity interface on root / and fallback
"""

import os
import sys
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.inference_engine import MobiURLInferenceEngine

app = FastAPI(
    title="MobiURL-Guard API",
    description="Explainable, Calibrated and Privacy-Aware Malicious URL Threat Detection",
    version="1.0.0"
)

# Initialize engine once at serverless cold start
model_path = os.path.join("models", "exported", "best_student_model.json")
brand_path = os.path.join("config", "brand_domains.json")
engine = MobiURLInferenceEngine(model_path=model_path, brand_config_path=brand_path)


class PredictRequest(BaseModel):
    url: str
    message_text: Optional[str] = None
    sender: Optional[str] = None
    channel: Optional[str] = None


def get_html_content() -> str:
    html_path = os.path.join(os.path.dirname(__file__), "..", "public", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MobiURL-Guard Threat Detection Engine Active</h1>"


@app.get("/api/health")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "MobiURL-Guard",
        "version": "1.0.0",
        "architecture": "Calibrated Compact Tree Ensemble",
        "offline_mobile_ready": True
    }


@app.post("/api/predict")
@app.post("/predict")
def predict(req: PredictRequest):
    result = engine.predict(
        url=req.url,
        message_text=req.message_text,
        sender=req.sender,
        channel=req.channel
    )
    return result


# Route root and common Vercel serverless path permutations
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=get_html_content(), status_code=200)


# Custom 404 handler to prevent {"detail":"Not Found"} on user visits
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if request.method == "GET" and not request.url.path.startswith("/api/predict"):
        return HTMLResponse(content=get_html_content(), status_code=200)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
