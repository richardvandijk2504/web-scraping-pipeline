import os
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Base-level Selenium Skeleton
#This skeleton is rather modular and can be converted to other web sources rather easily.

UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def open_browser(browser="chrome", headless=True, debug=False):
    """
    Opens a browser session (configured for PubMed scraping), ready to navigate pages. 
    Headless mode can be enabled for running without a visible window, and debug mode
    prints initialization info. Returns a Selenium driver object ready to use.
    
    Raises ValueError if an unsupported browser is specified.
    """
    
    if browser.lower() == "chrome":
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        user_agent = random.choice(UA)
        options.add_argument(f"--user-agent={user_agent}")
        driver = webdriver.Chrome(service=ChromeService(), options=options)

    elif browser.lower() == "edge":
        from selenium.webdriver.edge.options import Options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        user_agent = random.choice(UA)
        options.add_argument(f"--user-agent={user_agent}")
        driver = webdriver.Edge(service=EdgeService(), options=options)

    else:
        raise ValueError(f"You've entered an unsupported browser: {browser}. Use 'chrome' or 'edge'.")

    

    if debug:
        logging.info(f"{browser.capitalize()} browser opened w/ User-Agent: {user_agent} (headless={headless})")
        
    return driver

def wait_for_el(driver, select_el, by="css", timeout=10):
    """
    Waits for a specific PubMed element, select_el, to appear on the HTML page.
    Selector can be 'css' (string) or 'xpath' (expression). Returns the web element if found,
    otherwise logs a warning to console and returns None. Timeout default is 10 seconds.
    """
    by_type = By.CSS_SELECTOR if by == "css" else By.XPATH
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by_type, select_el))
        )
        return el
    
    except Exception as err:
        logging.warning(f"Element '{select_el}' not found within {timeout}s. Error: {err}")
        return None

def close_browser(driver):
    """
    Closes the PubMed browser session cleanly.
    Logs success or any errors encountered during quit.
    """
    if not driver:
        logging.warning("No driver to close.")
        return
    try:
        driver.quit()
        logging.info("Browser session closed successfully.")
    except Exception as err:
        logging.error(f"Error closing browser: {err}")
