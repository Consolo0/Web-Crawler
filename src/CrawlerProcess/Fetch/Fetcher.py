from typing import Optional
import requests
import time
import random
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
        # Create session for connection pooling and cookie handling
        self.session = requests.Session()
        self.session.headers.update(self._get_realistic_headers())
        
        # Delay between requests to avoid bot detection
        self.min_delay = 1.0
        self.max_delay = 2.0
        self.last_request_time = 0

    def _get_realistic_headers(self) -> dict:
        """
        Return realistic browser headers to avoid bot detection.
        These headers mimic a real Chrome browser request.
        """
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def _add_delay(self):
        """
        Add random delay between requests to mimic human behavior.
        This helps avoid triggering bot detection.
        """
        elapsed = time.time() - self.last_request_time
        delay_needed = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < delay_needed:
            sleep_time = delay_needed - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def fetch(self, url: str, uses_js: bool) -> str:

        if uses_js:
            return self._fetch_with_js(url)
        return self._fetch_without_js(url)

    def _fetch_without_js(self, url: str) -> str:
        """
        Fetch page without JavaScript execution.
        Uses requests with realistic headers and delays.
        """
        self._add_delay()
        
        try:
            response = self.session.get(
                url,
                timeout=self.timeout_seconds,
                allow_redirects=True,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def _fetch_with_js(self, url: str) -> str:
        """
        Fetch page with JavaScript execution using Playwright.
        Includes anti-bot measures and realistic browser behavior.
        """
        self._add_delay()
        
        try:
            with sync_playwright() as p:
                # Launch browser with anti-detection flags
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                    ]
                )
                
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                )
                
                # Add header to hide Playwright detection
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => false })")
                
                page = context.new_page()
                
                # Intercept and handle requests realistically
                page.set_extra_http_headers(self._get_realistic_headers())

                try:
                    page.goto(
                        url,
                        timeout=self.timeout_seconds * 1000,
                        wait_until="networkidle",
                    )
                except Exception as e:
                    # If networkidle times out, try with domcontentloaded (faster)
                    try:
                        page.goto(
                            url,
                            timeout=self.timeout_seconds * 1000,
                            wait_until="domcontentloaded",
                        )
                    except Exception as e2:
                        # If still timing out, just load what's there
                        print(f"Timeout loading {url}: {e2}")
                        pass
                
                # Simulate human behavior - scroll and wait
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(random.uniform(0.5, 1.5))

                html = page.content()
                browser.close()
                return html
        
        except Exception as e:
            print(f"Error fetching with JS {url}: {e}")
            return ""
