import scrapy


class HekamSpider(scrapy.Spider):
    name = "hekam"
    allowed_domains = ["kalemtayeb.com"]
    start_urls = ["https://kalemtayeb.com/hekam/"]

    def parse(self, response):
        pass
