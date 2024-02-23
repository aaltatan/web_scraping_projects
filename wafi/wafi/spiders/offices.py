import scrapy
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

class OfficesSpider(scrapy.Spider):
    name = "offices"
    allowed_domains = ["wafi.housing.gov.sa"]
    start_urls = ["https://wafi.housing.gov.sa/offices"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('.views-field-title a::attr(href)').getall()
        for link in links:
            yield res.follow(url=res.urljoin(link), callback=self.parse_page)
        
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield res.follow(url=next_page, callback=self.parse)

    def parse_page(self, res: Response):
        response: scrapy.Selector = res
        fields = response.css('.field')

        information: dict = {}
        for f in fields:
            key = (
                f
                .css('.field-label::text')
                .get('')
                .strip()
                .replace(':', '')
            )
            value = f.css('.field-items *::text').getall()
            value = "".join(value)
            information[key] = value

        yield {
            'title': response.css('.breadcrumb li.active::text').get(),
            **information
        }

