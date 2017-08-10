import sys
import scrapy
import json
from scrapy.crawler import CrawlerProcess

class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class ZefixSpider(scrapy.Spider):
    name = 'zefix'
    allowed_domains = ['zefix.ch']
    view_base_url    = "https://www.zefix.ch/ZefixREST/api/v1/firm/%s.json"
    listing_base_url = "https://www.zefix.ch/ZefixREST/api/v1/firm/search.json"

    start_urls = ['https://www.zefix.ch/ZefixREST/api/v1/firm/search.json']
    headers = {'Content-Type': 'application/json'}

    # TODO: add all 3 character permutations
    search_queries = ['aaa']
    max_entries = 30

    custom_settings = {
        'ITEM_PIPELINES': {
            'zefix_crawler.JsonWriterPipeline': 1
        }
    }

    def start_requests(self):
        for search_query in self.search_queries:
            params = {'name': search_query, 'maxEntries': self.max_entries, 'offset': 0}
            yield scrapy.Request(self.listing_base_url,
                                 method='POST',
                                 body=json.dumps(params),
                                 headers=self.headers,
                                 callback=self.parse_listing,
                                 errback=self.errback_listing)

    def parse_listing(self, response):
        self.logger.info("Parsing listing")

        doc = json.loads(response.body_as_unicode())
        # * yield a bunch of view requests
        for item in doc['list']:
            nextUrl = self.view_base_url % item['ehraid']
            yield response.follow(nextUrl, callback=self.parse_view)

        # * yield a pageinated view request
        if doc['hasMoreResults']:
            next_offset = doc['offset'] + self.max_entries
            params = {'name': "aaa", 'maxEntries': self.max_entries, 'offset': next_offset}
            yield scrapy.Request(self.listing_base_url,
                                method='POST',
                                headers=self.headers,
                                body=json.dumps(params),
                                callback=self.parse_listing,
                                errback=self.errback_listing)

    def parse_view(self, response):
        self.logger.info("Parsing view")
        doc = json.loads(response.body_as_unicode())
        yield doc

    def errback_listing(self, failure):
        self.logger.info("Error on parsing listing")

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    process = CrawlerProcess()

    process.crawl(ZefixSpider)
    process.start()

if __name__ == "__main__":
    main()
