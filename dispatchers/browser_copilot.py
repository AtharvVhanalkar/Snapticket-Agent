import webbrowser
import subprocess
from typing import Dict, Any

class BrowserCopilot:
    """
    Coordinates web form autofill for third-party support portals.
    Features automated URL sanitation and native browser + clipboard fallback.
    """
    def __init__(self, target_url: str):
        target = target_url.strip()
        # Automatically format bare repo names into GitHub issue URLs
        if "/" in target and not target.startswith("http"):
            self.target_url = f"https://github.com/{target}/issues/new"
        elif not target.startswith("http"):
            self.target_url = f"https://{target}"
        else:
            self.target_url = target

    def autofill_form(self, title: str, description: str) -> Dict[str, Any]:
        full_text = f"{title}\n\n{description}"
        
        # 1. Always copy report text to macOS clipboard (pbcopy)
        try:
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(full_text.encode("utf-8"))
        except Exception:
            pass

        # 2. Try launching Playwright Chromium automation
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto(self.target_url, wait_until="domcontentloaded")

                for sel in ['input[name*="title" i]', 'input[name*="subject" i]', 'input[id*="summary" i]', 'input[id*="issue_title" i]']:
                    if page.locator(sel).count() > 0:
                        page.locator(sel).first.fill(title)
                        break

                for sel in ['textarea[name*="desc" i]', 'textarea[name*="body" i]', 'div[contenteditable="true"]', 'textarea[id*="issue_body" i]']:
                    if page.locator(sel).count() > 0:
                        page.locator(sel).first.fill(description)
                        break

                # Hold open for review
                page.wait_for_timeout(25000)
                browser.close()
                return {"status": "success", "message": f"Autofilled form at {self.target_url}"}
        except Exception:
            # 3. Fallback: Launch default browser to target URL
            webbrowser.open(self.target_url)
            return {
                "status": "success",
                "message": f"Browser opened to {self.target_url}. Bug report copied to clipboard—paste with Cmd+V!"
            }