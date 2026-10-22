import os
import base64
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, Any, Optional

class GemmaEngine:
    def __init__(self):
        self.use_local = os.getenv("USE_LOCAL_GEMMA", "true").lower() == "true"
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "iandiii/gemma4-e4b-hermes-64k")
        self.api_key = os.getenv("GEMMA_API_KEY", "")

    def preprocess_image(self, image_bytes: bytes, max_dim: int = 1280) -> str:
        """Downscales Retina display screenshots to prevent VRAM allocation spikes."""
        img = Image.open(BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        width, height = img.size
        if max(width, height) > max_dim:
            scale = max_dim / float(max(width, height))
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def synthesize_report(self, image_bytes: Optional[bytes], telemetry_text: Optional[str]) -> str:
        prompt = (
            "You are an automated bug triage engineer. Analyze the provided crash data and/or screenshot.\n"
            "Return a strictly valid JSON object with the following fields:\n"
            "{\n"
            '  "title": "Concise issue title with error or component name",\n'
            '  "app_name": "Target application name",\n'
            '  "reproduction_steps": ["Step 1", "Step 2", "Step 3"],\n'
            '  "expected_behavior": "What should have occurred",\n'
            '  "actual_behavior": "Observed failure or glitch",\n'
            '  "technical_diagnostics": "Root cause summary from logs or UI traces"\n'
            "}\n"
            "Do not include conversational preambles. Output raw JSON only."
        )

        b64_img = self.preprocess_image(image_bytes) if image_bytes else None

        if self.use_local:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt + (f"\n\nTelemetry Logs:\n{telemetry_text}" if telemetry_text else ""),
                "stream": False,
                "format": "json"
            }
            if b64_img:
                payload["images"] = [b64_img]
            
            resp = requests.post(f"{self.ollama_host}/api/generate", json=payload, timeout=60)
            return resp.json().get("response", "{}")
        else:
            # Cloud API fallback (Google AI Studio)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            parts = [{"text": prompt + (f"\n\nTelemetry Logs:\n{telemetry_text}" if telemetry_text else "")}]
            if b64_img:
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64_img}})
            
            resp = requests.post(url, json={"contents": [{"parts": parts}]}, timeout=30)
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]