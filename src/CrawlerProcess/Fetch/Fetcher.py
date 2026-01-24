from typing import Optional
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


class Fetcher:

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

        if uses_js:
            return BeautifulSoup(self._fetch_with_js(url), "html.parser")
        return BeautifulSoup(self._fetch_without_js(url), "html.parser")

    def _fetch_without_js(self, url: str) -> str:

        response = requests.get(
            url,
            timeout=self.timeout_seconds,
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()
        return response.text

    def _fetch_with_js(self, url: str) -> str:

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
