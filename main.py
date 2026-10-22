import os
import json
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from core.log_sensor import MacOSLogSensor
from core.gemma_engine import GemmaEngine
from core.report_builder import ReportBuilder
from dispatchers.github_client import GitHubDispatcher
from dispatchers.browser_copilot import BrowserCopilot

app = FastAPI(title="SnapTicket Agent API")
sensor = MacOSLogSensor()
engine = GemmaEngine()

ui_dir = Path(__file__).resolve().parent / "ui"
app.mount("/static", StaticFiles(directory=str(ui_dir)), name="static")

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
async def analyze_report(
    image: Optional[UploadFile] = File(None),
    use_telemetry: bool = Form(True)
):
    img_bytes = await image.read() if image else None
    telemetry_data = sensor.fetch_latest_incident() if use_telemetry else None
    telemetry_text = telemetry_data.get("telemetry", "") if telemetry_data else ""

    raw_response = engine.synthesize_report(img_bytes, telemetry_text)
    try:
        parsed_json = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
    except Exception:
        parsed_json = {
            "title": "Application Exception Detected",
            "actual_behavior": raw_response,
            "reproduction_steps": ["Trigger application crash event"],
            "expected_behavior": "Expected stable execution",
            "technical_diagnostics": "Telemetry trace captured from host logs."
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
        res = dispatcher.create_issue(target, title, body)
        return res
    else:
        copilot = BrowserCopilot(target)
        res = copilot.autofill_form(title, body)
        return res

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)