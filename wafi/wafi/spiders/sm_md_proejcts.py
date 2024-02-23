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


class SmMdProjectsSpider(scrapy.Spider):
    name = "sm_md_projects"
    allowed_domains = ["wafi.housing.gov.sa"]
    start_urls = ["https://wafi.housing.gov.sa/ar/small_medium_projects"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('.field-content > a::attr(href)').getall()
        for link in links:
            yield res.follow(url=link, callback=self.parse_project)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield res.follow(url=next_page, callback=self.parse)

    def parse_project(self, res: Response):
        response: scrapy.Selector = res

        information: dict = {}

        fields = response.css('.field')
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