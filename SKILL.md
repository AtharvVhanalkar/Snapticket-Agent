# Agent Skill: SnapTicket Triage Agent

## Specification
- **Agent Name:** SnapTicket Autonomous Triage Agent
- **Target Architecture:** Local-First Multimodal Incident Reporter
- **Engine Core:** Gemma 4 (`gemma4-e4b-hermes-64k` / Cloud BYOK Fallback)
- **Host OS Target:** macOS DiagnosticReports (`.ips`)

## Trigger Conditions
1. **Visual Glitch Trigger:** User provides a screen capture showing an anomalous UI state, render failure, or frontend error.
2. **System Incident Trigger:** Host OS logs an unhandled exception or crash event in `~/Library/Logs/DiagnosticReports/*.ips` within the preceding 15-minute operational window.
3. **Manual CLI / API Triage:** Direct programmatic invocation via `POST /api/analyze`.

## Capabilities & Tool Pipeline
- **Telemetry Ingestion:** `core/log_sensor.py` extracts stack traces, faulting threads, and register dumps from native macOS crash reports without running background daemons.
- **Multimodal Synthesis:** `core/gemma_engine.py` correlates visual error cues with raw crash dumps in a single inference pass, downscaling Retina screenshots to 1280px to protect host VRAM.
- **Data Sovereignty Gate:** Enforces a binary privacy choice (`Attach Screenshot` vs. `Text-Only Diagnostics`) prior to external dispatch.
- **Dual-Channel Dispatch:**
  - **Channel A (GitHub Issues API):** Authenticated issue publication via `dispatchers/github_client.py`.
  - **Channel B (Browser Co-Pilot):** Human-assisted form population via `dispatchers/browser_copilot.py` with native clipboard fallback (`pbcopy`) for CAPTCHA-gated web portals.

## Operational Safety & Compliance
- Zero unmonitored filesystem mutation.
- Local secrets isolated in `.env` and omitted from version control via `.gitignore`.
- Deterministic log evidence grounding prevents probabilistic hallucination.