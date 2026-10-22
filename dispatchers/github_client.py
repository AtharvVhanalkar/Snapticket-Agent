import os
import requests
from typing import Dict, Any, Optional

class GitHubDispatcher:
    """
    Dispatches structured bug reports directly to target repositories
    using authenticated GitHub REST API endpoints.
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")

    def create_issue(self, repo: str, title: str, body: str) -> Dict[str, Any]:
        if not self.token:
            return {"status": "error", "message": "Missing GITHUB_TOKEN in environment configuration."}

        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }
        payload = {"title": title, "body": body}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 201:
                data = response.json()
                return {
                    "status": "success",
                    "url": data.get("html_url"),
                    "number": data.get("number")
                }
            return {
                "status": "error",
                "code": response.status_code,
                "message": response.text
            }
        except Exception as e:
            return {"status": "error", "message": f"Connection exception: {str(e)}"}