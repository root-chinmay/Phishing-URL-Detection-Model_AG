"""
Vercel Serverless API Handler for MobiURL-Guard.
Provides RESTful endpoints for online demo and API access:
- POST /api/predict: Analyzes URL and returns calibrated threat breakdown
- GET /api/health: Health check and model metadata
- Serves interactive cybersecurity interface on root /
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


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "MobiURL-Guard",
        "version": "1.0.0",
        "architecture": "Calibrated Compact Tree Ensemble",
        "offline_mobile_ready": True
    }


@app.post("/api/predict")
def predict(req: PredictRequest):
    result = engine.predict(
        url=req.url,
        message_text=req.message_text,
        sender=req.sender,
        channel=req.channel
    )
    return result


@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MobiURL-Guard | Mobile Malicious URL Threat Detection</title>
  <style>
    :root {
      --bg: #0b132b;
      --surface: #1c2541;
      --primary: #00b4d8;
      --text: #f0f4f8;
      --muted: #8d99ae;
      --danger: #e63946;
      --warning: #f4a261;
      --success: #2a9d8f;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); min-height: 100vh; padding: 2rem 1rem; display: flex; flex-direction: column; align-items: center; }
    .container { max-width: 720px; width: 100%; }
    .badge { display: inline-block; background: rgba(42, 157, 143, 0.2); color: var(--success); padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 1px; margin-bottom: 0.5rem; }
    h1 { font-size: 2rem; color: var(--primary); margin-bottom: 0.25rem; }
    p.sub { color: var(--muted); font-size: 0.95rem; margin-bottom: 2rem; }
    .card { background: var(--surface); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); }
    label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--muted); margin-bottom: 0.5rem; }
    input[type="text"] { width: 100%; padding: 0.85rem 1rem; background: #0e172f; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text); font-size: 1rem; margin-bottom: 1rem; }
    input[type="text"]:focus { outline: none; border-color: var(--primary); }
    button { background: var(--primary); color: #0b132b; border: none; padding: 0.85rem 1.5rem; border-radius: 8px; font-weight: 700; font-size: 1rem; cursor: pointer; width: 100%; transition: opacity 0.2s; }
    button:hover { opacity: 0.9; }
    .result-box { display: none; margin-top: 1.5rem; }
    .risk-banner { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem; border-radius: 8px; margin-bottom: 1rem; background: rgba(0,0,0,0.2); }
    .risk-score { font-size: 2.5rem; font-weight: 800; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
    .stat { background: #0e172f; padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); }
    .stat-val { font-size: 1.1rem; font-weight: 700; margin-top: 0.25rem; }
    .reasons { background: #0e172f; padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: var(--muted); }
    .reasons ul { padding-left: 1.25rem; margin-top: 0.5rem; }
    .reasons li { margin-bottom: 0.4rem; color: var(--text); }
  </style>
</head>
<body>
  <div class="container">
    <span class="badge">OFFLINE-CAPABLE MOBILE ENGINE</span>
    <h1>MobiURL-Guard</h1>
    <p class="sub">Explainable, Calibrated and Adversarially Robust Mobile Malicious URL Detection Framework</p>

    <div class="card">
      <label>TARGET URL TO ANALYSE</label>
      <input type="text" id="urlInput" value="https://paypal.com.account-verify.test/login" placeholder="https://example.com/verify">
      <label>OPTIONAL MESSAGE CONTEXT (SMS / WhatsApp)</label>
      <input type="text" id="msgInput" placeholder="e.g. Urgent! Your account is suspended, click link to verify now">
      <button onclick="analyzeUrl()">ANALYSE THREAT PROFILE</button>

      <div class="result-box" id="resultBox">
        <div class="risk-banner" id="riskBanner">
          <div>
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;" id="riskCat">Risk Category</div>
            <div style="font-size: 1.25rem; font-weight: 700;" id="riskDecision">Decision</div>
          </div>
          <div class="risk-score" id="riskScore">0%</div>
        </div>

        <div class="grid">
          <div class="stat">
            <div style="font-size: 0.75rem; color: var(--muted);">ESTIMATED BENIGN PROBABILITY</div>
            <div class="stat-val" id="benignProb">0%</div>
          </div>
          <div class="stat">
            <div style="font-size: 0.75rem; color: var(--muted);">CONFORMAL PREDICTION SET</div>
            <div class="stat-val" id="conformalSet">{Legitimate}</div>
          </div>
          <div class="stat">
            <div style="font-size: 0.75rem; color: var(--muted);">MODEL CONFIDENCE</div>
            <div class="stat-val" id="modelConf">High</div>
          </div>
          <div class="stat">
            <div style="font-size: 0.75rem; color: var(--muted);">UNCERTAINTY STATUS</div>
            <div class="stat-val" id="uncStatus">Certain</div>
          </div>
        </div>

        <div class="reasons">
          <strong>Key Influential Risk Indicators (Explainable AI):</strong>
          <ul id="reasonsList"></ul>
        </div>
      </div>
    </div>
  </div>

  <script>
    async function analyzeUrl() {
      const url = document.getElementById('urlInput').value.trim();
      const msg = document.getElementById('msgInput').value.trim();
      if(!url) return;
      try {
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({url: url, message_text: msg || null})
        });
        const data = await res.json();
        
        document.getElementById('resultBox').style.display = 'block';
        document.getElementById('riskScore').innerText = data.risk_percentage.toFixed(1) + '%';
        document.getElementById('riskDecision').innerText = data.classification.toUpperCase();
        document.getElementById('benignProb').innerText = (data.benign_probability * 100).toFixed(1) + '%';
        document.getElementById('conformalSet').innerText = '{' + data.conformal_prediction_set.join(', ') + '}';
        document.getElementById('modelConf').innerText = data.prediction_confidence.toUpperCase();
        document.getElementById('uncStatus').innerText = data.uncertainty_status;

        const banner = document.getElementById('riskBanner');
        if (data.classification === 'malicious') {
          banner.style.borderLeft = '6px solid var(--danger)';
          document.getElementById('riskScore').style.color = 'var(--danger)';
          document.getElementById('riskCat').innerText = 'MALICIOUS THREAT DETECTED';
        } else if (data.classification === 'uncertain') {
          banner.style.borderLeft = '6px solid var(--primary)';
          document.getElementById('riskScore').style.color = 'var(--primary)';
          document.getElementById('riskCat').innerText = 'UNCERTAIN / INSUFFICIENT EVIDENCE';
        } else {
          banner.style.borderLeft = '6px solid var(--success)';
          document.getElementById('riskScore').style.color = 'var(--success)';
          document.getElementById('riskCat').innerText = 'LIKELY SAFE / LEGITIMATE';
        }

        const list = document.getElementById('reasonsList');
        list.innerHTML = '';
        data.top_reasons.forEach(r => {
          const li = document.createElement('li');
          li.innerText = r;
          list.appendChild(li);
        });
      } catch(e) {
        alert('Error communicating with detection engine: ' + e);
      }
    }
  </script>
</body>
</html>
"""
    return html_content
