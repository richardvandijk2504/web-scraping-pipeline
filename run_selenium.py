import argparse
import os
import random
import time
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium_scripts.selenium_dynamic import fetch_art, save_json, concat_raw

#TO ADD Anti-scraping countermeasures & data format validation

desired_attr = [
    ("title", "a.docsum-title", None, "warning", None),
    ("link", "a.docsum-title", "href", "warning",
     lambda x: f"https://pubmed.ncbi.nlm.nih.gov{x}" if x and not x.startswith("http") else x),
    ("authors", "span.docsum-authors.full-authors", None, "debug", None),
    ("journal", "span.docsum-journal-citation.full-journal-citation", None, "warning", None),
    ("year", "span.docsum-journal-citation.full-journal-citation", None, "warning",
     lambda x: re.search(r"\b(\d{4})\b", x).group(1) if x and re.search(r"\b(\d{4})\b", x) else None),
    ("pmid", "span.docsum-pmid", None, "error", None)
]

def scraper(start_date, end_date, base_url, headless=True, debug=False):
    """
    Scrapes all PubMed articles in a timeframe and saves JSON into data/sel_temp/
    
    !!Note that temp files need to be deleted manually, add bool_var to toggle auto deletion
    """
    start_str = start_date.strftime("%Y/%m/%d")
    end_str = end_date.strftime("%Y/%m/%d")

    temp_data = fetch_art(base_url, start_str, end_str, headless=headless, debug=debug)

    output_folder = "data"
    temp_folder = os.path.join(output_folder, "sel_temp")
    os.makedirs(temp_folder, exist_ok=True)

    temp_file = os.path.join(temp_folder, f"pubmed_{start_str.replace('/','-')}_to_{end_str.replace('/','-')}.json")
    save_json(temp_data, temp_file)
    
    time.sleep(random.uniform(1.5, 3.5))

    if debug:
        print(f"Saved intermediate (temp) JSON: {temp_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--parallel", type=int, default=5, help="Number of weeks to scrape in parallel")
    args = parser.parse_args()

    base_url = "https://pubmed.ncbi.nlm.nih.gov/?term=Biology"
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)

    start_date = datetime(2000, 1, 1)     
    end_date = datetime(2000, 1, 7)        
    chunk_size = timedelta(days=7)          

    date_chunks = []  
    cur_date = start_date  

    while cur_date <= end_date: 
        chunk_start = cur_date
        chunk_end = min(cur_date + chunk_size - timedelta(days=1), end_date)
        date_chunks.append((chunk_start, chunk_end))
        cur_date = chunk_end + timedelta(days=1)

    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = [
            executor.submit(
                scraper,                    
                start,
                end,
                base_url,
                args.headless,
                args.debug
            )
            for start, end in date_chunks
        ]

        for future in as_completed(futures):
            future.result() 


    combined_data = concat_raw(os.path.join(output_folder, "sel_temp"))
    combined_file = os.path.join(output_folder, "pubmed_combined.json")
    save_json(combined_data, combined_file)

    if args.debug:
        print(f"Combined JSON saved: {combined_file}")

if __name__ == "__main__":
    main()
