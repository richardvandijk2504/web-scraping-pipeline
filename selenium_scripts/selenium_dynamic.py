import json
import os
import re
import time
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium_scripts.selenium_base import open_browser, wait_for_el, close_browser

#TO ADD: fallback selectors 

def extract_attr(art, selector, attr=None, field_name="", log_lvl="warning"):
    """
    Extracts attribute from a web element with ('css' or 'xpath') selector.
    Returns the extracted value or None if not found.
    """
    try:
        el = art.find_element(By.CSS_SELECTOR, selector)
        return el.get_attribute(attr).strip() if attr else el.text.strip()
    except (NoSuchElementException, StaleElementReferenceException): 
        logging.warning(f"{field_name} missing")
        return None
    except Exception as err:
        logging.error(f"Extraction of {field_name} failed. Error: {err}")
        return None


def fetch_art(base_url, start_date, end_date, desired_attr, browser="chrome",
              headless=True, debug=False, page_max=None):
    """
    Starts a Selenium driver (open_browser) and collects (PubMed) articles between a set start 
    and end date, returning a list of paginated article metadata. For each page in the date range, 
    extracts the attributes (defined w/ extract_art) for every article found.
    """
    driver = open_browser(browser, headless, debug)
    art_list = []

    try:
        page_cnt = 1
        while True:
            url = f"{base_url}&filter=dates.{start_date}-{end_date}&sort=pubdate&size=200&page={page_cnt}"
            logging.info(f"Fetching page {page_cnt}, published between {start_date} and {end_date}: {url}")

            driver.get(url)
            page_check = wait_for_el(driver, "div.docsum-content", by="css", timeout=10)
            if not page_check:
                logging.info("No results found on page or timed out.")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
            time.sleep(1)

            art_page = driver.find_elements(By.CSS_SELECTOR, "div.docsum-content")
            if not art_page:
                logging.info("End of page results reached.")
                break

            for art in art_page:
                record = {}
                for field_name, selector, attr, log_lvl, post_process in desired_attr:
                    extr_attr = extract_attr(art, selector, attr, field_name.capitalize(), log_lvl)
                    if post_process:
                        try:
                            pproc_attr = post_process(extr_attr)
                        except Exception as err:
                            logging.warning(f"Post-processing failed for {field_name}: {err}")
                            pproc_attr = None
                    record[field_name] = pproc_attr

                art_list.append(record)

            if page_max and page_cnt >= page_max:
                break

            page_cnt += 1

    finally:
        close_browser(driver)

    logging.info(f"Total articles collected between {start_date}–{end_date}: {len(art_list)}")
    return art_list

def save_json(data, filepath):
    """
    Saves scraped (PubMed) raw data as JSON file in the specified filepath.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def concat_raw(temp_folder):
    """
    Open and reads all JSON files in a temp folder (in this use-case, data/sel_temp/), after which
    it combines them into a single list. Returns the JSON for this combined list.
    """
    combined = []
    for file in os.listdir(temp_folder):
        if file.endswith(".json"):
            file_path = os.path.join(temp_folder, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        combined.extend(data)
                    else:
                        combined.append(data)
            except Exception as err:
                logging.warning(f"Failed to load {file}: {err}")
    return combined
