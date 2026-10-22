import os
import glob
import time
from pathlib import Path
from typing import Optional, Dict

class MacOSLogSensor:
    """
    Monitors macOS ~/Library/Logs/DiagnosticReports/ for native .ips
    and .crash incident files generated during application crashes.
    """
    def __init__(self, search_window_minutes: int = 15):
        self.search_window = search_window_minutes * 60
        self.diag_dir = Path.home() / "Library" / "Logs" / "DiagnosticReports"

    def fetch_latest_incident(self) -> Optional[Dict[str, str]]:
        if not self.diag_dir.exists():
            return None

        # Search for both modern macOS .ips and legacy .crash files
        incident_files = list(self.diag_dir.glob("*.ips")) + list(self.diag_dir.glob("*.crash"))
        if not incident_files:
            return None

        # Identify the newest file by modification timestamp
        latest_file = max(incident_files, key=os.path.getmtime)
        file_age = time.time() - os.path.getmtime(latest_file)

        # Check if the incident occurred within the active time window
        if file_age <= self.search_window:
            try:
                with open(latest_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(5000)  # Read top 5KB containing crash headers and trace
                return {
                    "source": "macOS DiagnosticReports",
                    "filename": latest_file.name,
                    "age_seconds": int(file_age),
                    "telemetry": content
                }
            except Exception as e:
                return {
                    "source": "macOS DiagnosticReports",
                    "error": f"Failed reading log: {str(e)}"
                }
        return None

if __name__ == "__main__":
    sensor = MacOSLogSensor(search_window_minutes=60)
    incident = sensor.fetch_latest_incident()
    if incident:
        print(f"[+] Detected incident: {incident['filename']}")
    else:
        print("[-] No incident reports detected within the specified time window.")