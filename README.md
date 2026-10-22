# SnapTicket Agent 🎫⚡
> **Autonomous, privacy-first incident triage agent powered by Gemma 4.**

SnapTicket bridges the gap between chaotic client-side runtime crashes and structured engineering issue trackers. By uniting low-level OS diagnostic telemetry (macOS DiagnosticReports `.ips`) with visual error screenshots, SnapTicket uses **Gemma 4** to eliminate ambiguous bug reports, diagnose root causes in seconds, and stage or dispatch production-ready tickets directly to issue backends or web portals.

---

> ⚠️ **Project Status: Active Demo / Hackathon Proof-of-Concept**  
> SnapTicket Agent is currently operating in a **live demonstration phase**. Real-time GitHub API issue creation is fully operational with valid tokens, while third-party web portal submission runs through an assisted browser co-pilot / clipboard sync procedure to navigate authentication, bot protections (Cloudflare/CAPTCHA), and varied DOM structures safely.

---

### 💡 The Core Problem: The "It Crashed" Dilemma

When an application fails, developers face two extremes:
* **End-user bug reports are vague:** A screenshot or a message saying *"The screen froze"* lacks stack traces, exception codes, faulting thread dumps, and system architecture details.
* **Crash logs are inscrutable to non-engineers:** Native OS diagnostic logs (`.ips` reports) contain invaluable post-mortem information—memory registers, exception vectors, dyld images—but are buried in raw JSON/text files deep inside system directories (`~/Library/Logs/DiagnosticReports/`).

Triaging these requires tedious manual correlation: matching when the user took the screenshot with which thread faulted in the logs, deducing the offending application component, and formatting it into a reproducible ticket.

---

### ⚡ The Idea: Autonomous Telemetry & Visual Fusion

SnapTicket Agent automates this triage pipeline using a local-first, multimodal approach:

```text
┌────────────────────────┐      ┌──────────────────────────────────┐
│ Visual Glitch Capture  │  +   │ macOS Telemetry (.ips Log Trace) │
│ (Retina Screenshot)    │      │ (Faulting Thread, Exception Code)│
└───────────┬────────────┘      └────────────────┬─────────────────┘
            │                                    │
            └─────────────────┬──────────────────┘
                              ▼
        ┌──────────────────────────────────────────────┐
        │        Gemma 4 Multimodal Reasoning          │
        │  - Correlates UI error state with log dumps  │
        │  - Identifies target app category (Native/3rd)│
        │  - Formats reproduction steps & diagnostics  │
        │  - Dynamically deduces canonical portal URL  │
        └─────────────────────┬────────────────────────┘
                              ▼
        ┌──────────────────────────────────────────────┐
        │       Privacy & Consent Control Studio       │
        │   [Attach Visual Evidence] vs [Text Only]    │
        └─────────────────────┬────────────────────────┘
                              ▼
                 Automated Dispatch Pipeline
                 ├── Channel A: Authenticated GitHub REST API
                 └── Channel B: Human-Assisted Web Portal Co-Pilot