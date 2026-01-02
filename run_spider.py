import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_scripts.scrapy_base import create_script

#Ensure that the output folder exists
os.makedirs("data", exist_ok=True)
name="publications_2024"
urls=["https://api.openalex.org/works?filter=publication_year:2024"]

#Generate a spider class
Publications2024Spider = create_script(
    name,
    urls,
    debug=True
)

#Setup Crawler and run
process = CrawlerProcess(settings={
    "FEEDS": {
        "data/publications_2024.json": {"format": "json", "encoding": "utf8", "indent": 2}
    },
    "LOG_LEVEL": "ERROR"
})

process.crawl(Publications2024Spider)
process.start()
print(f"Crawl completed. Output stored as data/{name}")