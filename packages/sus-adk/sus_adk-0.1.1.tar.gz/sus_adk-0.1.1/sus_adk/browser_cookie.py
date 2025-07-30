from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import time

def get_cookies_from_url(url: str, wait_time: int = 60, browser: str = 'chrome', headless: bool = False) -> Dict[str, str]:
    """
    Launch a browser, navigate to the URL, let the user log in, and extract cookies.
    browser: 'chrome', 'firefox', or 'edge'
    headless: run browser in headless mode
    wait_time: seconds to wait for user to complete login.
    Returns cookies as a dict.
    """
    driver = None
    if browser == 'chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_experimental_option("detach", not headless)
        driver = webdriver.Chrome(options=options)
    elif browser == 'firefox':
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
    elif browser == 'edge':
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    driver.get(url)
    print(f"Please log in to {url} in the opened browser window.")
    print(f"Waiting {wait_time} seconds for login...")
    time.sleep(wait_time)
    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    driver.quit()
    return cookies 