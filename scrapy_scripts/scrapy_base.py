import scrapy

def create_script(name, urls, debug):
    """
    Generates Spider classes for a given name and start url(s).
    """
    class DynamicSpiderClass(scrapy.Spider):
        """
        Inherited Scrapy "Spider" class, sends requests, follows links,
        handles responses, and exports results. Returns a Spider class.
        """
        def start_requests(self):
            for url in self.start_urls:
                yield scrapy.Request(url=url, callback=self.parse)

        def parse(self, response):
            data = response.json()['results']
            if self.debug:
                print(f"Received {len(data)} items from {response.url}")
            for item in data:
                yield {
                    "title": item.get("title"),
                    "authors": [a["author"]["display_name"] for a in item.get("authorships", [])],
                    "journal": item.get("host_venue", {}).get("display_name"),
                    "year": item.get("publication_year"),
                    "doi": item.get("doi"),
                    "citations": item.get("cited_by_count")
                }

    DynamicSpiderClass.name = name
    DynamicSpiderClass.start_urls = urls
    DynamicSpiderClass.debug = debug
    
    return DynamicSpiderClass 
