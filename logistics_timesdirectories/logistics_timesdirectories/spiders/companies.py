from scrapy.http import Request, Response, FormRequest
from fake_useragent import FakeUserAgent
from typing import Iterator, Iterable
import requests
import chompjs
import scrapy
import json
import re
import logging


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)

class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["logistics.timesdirectories.com"]

    def start_requests(self) -> list[Request]:
        BASE = "https://logistics.timesdirectories.com/company-listings"
        request = Request(url=BASE)
        request.meta['dont_cache'] = True
        return [request]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('.company-details > p > a::attr(href)').getall()
        for link in links:
            yield res.follow(url=res.urljoin(link), callback=self.parse_company)

        next_page = (
            response
            .xpath('//a[@aria-label="Next" and span[text()="Next" and @aria-hidden]]/@href')
            .extract_first()
        )
        if next_page:
            request = res.follow(url=res.urljoin(next_page), callback=self.parse)
            request.meta['dont_cache'] = True
            yield request

    def parse_company(self, res: Response):
        response: scrapy.Selector = res
        script = response.css('script[type="application/ld+json"]::text').get()
        data = chompjs.parse_js_object(script)
        yield data