# SnapTicket Agent 🎫⚡
> **Autonomous, privacy-first incident ingestion and triage agent powered by Gemma 4.**

SnapTicket bridges the gap between client-side crashes and engineering issue trackers. It correlates native host telemetry (macOS DiagnosticReports `.ips`) with visual error screenshots, synthesizes structured bug reports using **Gemma 4**, and dispatches them via GitHub REST API or human-assisted browser autofill.

---

## 🌟 Key Features

- **Multimodal Gemma 4 Core:** Runs locally via Ollama (`iandiii/gemma4-e4b-hermes-64k`) or through Google AI Studio API (Bring Your Own Key).
- **Native OS Telemetry Sensor:** Scans `~/Library/Logs/DiagnosticReports/` for recent incident dumps, extracting exact exception codes and stack traces.
- **Binary Privacy Consent Gate:** Lets users inspect diagnostic payloads and explicitly choose between attaching visual evidence or falling back to text-only diagnostics.
- **Dual-Channel Dispatcher:** 
  - Direct, authenticated **GitHub Issues API** integration.
  - **Browser Co-Pilot** (Playwright + native clipboard fallback) for web support portals requiring manual CAPTCHA solving.
- **Clean Light-Themed Dashboard:** Distraction-free, responsive UI built with Tailwind CSS.

---

## 🏗️ Architecture

```text
[User Screenshot]  +  [macOS DiagnosticReports (~/Library/Logs/.../*.ips)]
                                  │
                                  ▼
                   [core/gemma_engine.py: Gemma 4]
              (Multimodal Vision + Telemetry Reasoning)
                                  │
                                  ▼
             [UI Review Dashboard (Light-Mode Studio)]
         - Image Preview & Consent Gate ([Attach] vs [Omit])
         - Editable Markdown Bug Report
         - Target Destination Selector
                                  │
                                  ▼
                     [Dispatcher Selection]
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
        [GitHub REST API]            [Browser Co-Pilot]
     Live issue created on repo     Automated DOM form fill