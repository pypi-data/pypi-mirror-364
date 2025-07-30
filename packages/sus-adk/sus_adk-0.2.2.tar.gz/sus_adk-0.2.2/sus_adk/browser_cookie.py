from typing import Dict
from playwright.sync_api import sync_playwright
import time

def get_cookies_from_url(url: str, wait_time: int = 60, browser: str = 'chromium', headless: bool = False) -> Dict[str, str]:
    """
    Launch a browser, navigate to the URL, let the user log in, and extract cookies.
    browser: 'chromium', 'firefox', or 'webkit'
    headless: run browser in headless mode
    wait_time: seconds to wait for user to complete login.
    Returns cookies as a dict.
    """
    with sync_playwright() as p:
        browser_type = getattr(p, browser)
        browser_instance = browser_type.launch(headless=headless)
        context = browser_instance.new_context()
        page = context.new_page()
        page.goto(url)
        print(f"Please log in to {url} in the opened browser window.")
        print(f"Waiting {wait_time} seconds for login...")
        time.sleep(wait_time)
        cookies = context.cookies()
        browser_instance.close()
        return {cookie['name']: cookie['value'] for cookie in cookies} 