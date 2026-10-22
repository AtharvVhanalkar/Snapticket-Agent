import json
from typing import Dict, Any

class ReportBuilder:
    @staticmethod
    def build_markdown(structured_data: Dict[str, Any], include_telemetry: bool = True, telemetry_text: str = "") -> str:
        title = structured_data.get("title", "Unhandled Application Anomaly")
        steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(structured_data.get("reproduction_steps", []))])
        
        md = f"""# {title}

### 🐞 Bug Description
{structured_data.get("actual_behavior", "A crash or UI anomaly was detected.")}

### 🎯 Expected Behavior
{structured_data.get("expected_behavior", "Application executes without interruption.")}

### 📋 Steps to Reproduce
{steps if steps else "1. Launch target application.\\n2. Trigger anomaly action."}

### 🔍 Technical Diagnostics
{structured_data.get("technical_diagnostics", "No additional trace provided.")}
"""
        if include_telemetry and telemetry_text:
            md += f"\n### 📊 System Telemetry Log (macOS)\n```text\n{telemetry_text[:2000]}\n```\n"

        md += "\n---\n*Report generated autonomously by SnapTicket Agent via Gemma 4.*"
        return md