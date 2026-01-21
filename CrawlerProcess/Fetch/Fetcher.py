from typing import Optional
import requests
from playwright.sync_api import sync_playwright


class Fetcher:
    """
    Fetcher is responsible ONLY for retrieving HTML content.
    - If uses_js=False -> fast HTTP fetch using requests
    - If uses_js=True  -> JS-rendered fetch using Playwright
    """

    def __init__(
        self,
        timeout_seconds: int = 30,
        user_agent: Optional[str] = None
    ):
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def fetch(self, url: str, uses_js: bool) -> str:
        """
        Fetches HTML from the given URL.

        :param url: URL to fetch
        :param uses_js: whether the page requires JavaScript execution
        :return: rendered HTML as string
        """
        if uses_js:
            return self._fetch_with_js(url)
        return self._fetch_without_js(url)

    # -------------------------
    # Internal implementations
    # -------------------------

    def _fetch_without_js(self, url: str) -> str:
        """
        Fast path: plain HTTP fetch.
        """
        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()
        return response.text

    def _fetch_with_js(self, url: str) -> str:
        """
        JS-rendered fetch using Playwright.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=self.user_agent
            )
            page = context.new_page()

            page.goto(
                url,
                timeout=self.timeout_seconds * 1000,
                wait_until="networkidle",
            )

            html = page.content()

            browser.close()
            return html
