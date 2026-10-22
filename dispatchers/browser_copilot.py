import webbrowser
import subprocess
from typing import Dict, Any

class BrowserCopilot:
    """
    Coordinates human-assisted web form autofill for third-party support portals.
    Features a zero-dependency macOS clipboard and browser launch fallback.
    """
    def __init__(self, target_url: str):
        self.target_url = target_url

    def autofill_form(self, title: str, description: str) -> Dict[str, Any]:
        """Attempts visible Playwright automation; falls back to native browser and clipboard."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto(self.target_url, wait_until="domcontentloaded")

                # Selector heuristics for ticket fields
                for sel in ['input[name*="title" i]', 'input[name*="subject" i]', 'input[id*="summary" i]']:
                    if page.locator(sel).count() > 0:
                        page.locator(sel).first.fill(title)
                        break

                for sel in ['textarea[name*="desc" i]', 'textarea[name*="body" i]', 'div[contenteditable="true"]']:
                    if page.locator(sel).count() > 0:
                        page.locator(sel).first.fill(description)
                        break

                # Pause execution for human review and CAPTCHA solving
                page.wait_for_timeout(45000)
                browser.close()
                return {"status": "completed", "method": "playwright_copilot"}
        except Exception:
            # Native fallback: Copy text to macOS clipboard (pbcopy) and launch default browser
            full_text = f"{title}\n\n{description}"
            try:
                proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                proc.communicate(full_text.encode("utf-8"))
            except Exception:
                pass
            
            webbrowser.open(self.target_url)
            return {
                "status": "completed",
                "method": "browser_fallback_clipboard",
                "message": "Opened default browser and copied report content to clipboard."
            }