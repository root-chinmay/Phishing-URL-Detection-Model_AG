"""
Vercel Serverless API Handler for MobiURL-Guard.
Provides RESTful endpoints for online demo and API access:
- POST /api/predict, /predict, /: Analyzes URL and returns calibrated threat breakdown
- GET /api/health, /health: Health check and model metadata
- Serves interactive cybersecurity interface on root / and fallback
"""

import os
import sys
import json
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from src.models.inference_engine import MobiURLInferenceEngine

app = FastAPI(
    title="MobiURL-Guard API",
    description="Explainable, Calibrated and Privacy-Aware Malicious URL Threat Detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine once with absolute paths so serverless environment never fails to find files
model_path = os.path.join(BASE_DIR, "models", "exported", "best_student_model.json")
brand_path = os.path.join(BASE_DIR, "config", "brand_domains.json")
engine = MobiURLInferenceEngine(model_path=model_path, brand_config_path=brand_path)


class PredictRequest(BaseModel):
    url: str
    message_text: Optional[str] = None
    sender: Optional[str] = None
    channel: Optional[str] = None


def get_html_content() -> str:
    html_path = os.path.join(BASE_DIR, "public", "index.html")
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


# Universal POST handler catching any predict route permutation
@app.post("/api/predict")
@app.post("/predict")
@app.post("/api/index.py/api/predict")
@app.post("/api/index.py/predict")
@app.post("/api/index.py")
@app.post("/api")
@app.post("/")
async def universal_predict_endpoint(request: Request):
    try:
        body = await request.json()
        target_url = body.get("url", "").strip()
        if not target_url:
            return JSONResponse(
                status_code=400,
                content={"error": "Field 'url' is required and cannot be empty."}
            )

        msg = body.get("message_text")
        sender = body.get("sender")
        channel = body.get("channel")

        result = engine.predict(
            url=target_url,
            message_text=msg,
            sender=sender,
            channel=channel
        )
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )


# Universal GET handler serving the HTML dashboard
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
    if request.method == "POST":
        return await universal_predict_endpoint(request)
    return HTMLResponse(content=get_html_content(), status_code=200)
