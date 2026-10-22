import os
import json
from pathlib import Path
from typing import Optional

env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from core.log_sensor import MacOSLogSensor
from core.gemma_engine import GemmaEngine
from core.report_builder import ReportBuilder
from dispatchers.github_client import GitHubDispatcher
from dispatchers.browser_copilot import BrowserCopilot

app = FastAPI(title="SnapTicket Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sensor = MacOSLogSensor()
engine = GemmaEngine()

ui_dir = Path(__file__).resolve().parent / "ui"

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = ui_dir / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/detect-telemetry")
def detect_telemetry():
    incident = sensor.fetch_latest_incident()
    return {"detected": bool(incident), "incident": incident}

@app.post("/api/analyze")
def analyze_report(
    image: Optional[UploadFile] = File(None),
    use_telemetry: bool = Form(True),
    app_name: str = Form(""),
    app_type: str = Form("3rd_party")
):
    img_bytes = None
    if image:
        try:
            img_bytes = image.file.read()
        except Exception:
            img_bytes = None

    telemetry_data = sensor.fetch_latest_incident() if use_telemetry else None
    telemetry_text = telemetry_data.get("telemetry", "") if telemetry_data else ""

    raw_response = engine.synthesize_report(
        image_bytes=img_bytes,
        telemetry_text=telemetry_text,
        app_name=app_name,
        app_type=app_type
    )

    try:
        parsed_json = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
    except Exception:
        fallback_url = "https://feedbackassistant.apple.com" if app_type == "native_mac" else f"https://github.com/{os.getenv('GITHUB_DEFAULT_REPO', 'AtharvVhanalkar/snapticket-agent')}/issues"
        parsed_json = {
            "title": f"[{app_name or 'Application'}] Runtime Exception Detected",
            "actual_behavior": str(raw_response),
            "reproduction_steps": ["1. Launch application", "2. Trigger failure condition"],
            "expected_behavior": "Normal runtime execution",
            "technical_diagnostics": telemetry_text[:300] if telemetry_text else "Visual anomaly identified.",
            "suggested_portal_url": fallback_url
        }

    markdown_report = ReportBuilder.build_markdown(
        parsed_json,
        include_telemetry=use_telemetry,
        telemetry_text=telemetry_text
    )

    return {
        "structured": parsed_json,
        "markdown": markdown_report,
        "has_telemetry": bool(telemetry_data)
    }

@app.post("/api/dispatch")
def dispatch_issue(
    channel: str = Form(...),
    target: str = Form(...),
    title: str = Form(...),
    body: str = Form(...)
):
    if channel == "github":
        dispatcher = GitHubDispatcher()
        return dispatcher.create_issue(target, title, body)
    else:
        copilot = BrowserCopilot(target)
        return copilot.autofill_form(title, body)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)