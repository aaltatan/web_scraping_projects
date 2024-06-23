import scrapy


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["fnc-group.com"]
    start_urls = ["https://fnc-group.com/FNC-Group-Freight-Forwarder-Member-Directory"]

    def parse(self, response):
        pass
