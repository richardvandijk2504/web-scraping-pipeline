Web Scraping Pipeline using Scrapy/Selenium (in Development) (v0.1b)

Current Features:

- Scrapes static webpages using Scrapy and dynamic webpages using Selenium and outputs the (concatenated) raw data
in the ~/data/ folder.
- Supports parallelized Selenium scraping w/ configurable threads for fast extractions


Future Features:

- Automatically clean all raw data
- Improve anti-scraping countermeasures in run_selenium.py
- Add data format and required field schecks
- Add fallback (css and xpath) selector logic in selenium_dynamic.py
- Make source choices run modularly from a controller script  


Changelog:

* v0.1b:
    - Added randomized User Agents to selenium_base.py as to avoid scraping/ddos detection/protection
* v0.1a:
    - Base skeleton for Scrapy and Selenium pipelines made. 
    - Hardcoded support for OpenAlex (Scrapy) and PubMed (Selenium)
