import scrapy
from scrapy.http import Response, Request


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["businssdirectory.com"]
    start_urls = ["https://businssdirectory.com/wp-admin/admin-ajax.php"]

    def parse_company(self, res: Response):
        response: scrapy.Selector = res
        category = response.css('.list-category a::text').get()
        title = response.css('.list-heading *::text').get()
        posted_at = response.css('.list-posted-date::text').get()
        s = 'section.single-detail-page > .container > .row > div:first-child .panel-body p::text'
        description = (
            response
            .css(s)
            .get()
        )
