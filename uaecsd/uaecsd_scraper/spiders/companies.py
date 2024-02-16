from typing import Iterator
import scrapy
from scrapy.http import Response, Request
from urllib.parse import urlencode
from fake_useragent import FakeUserAgent
import json
import logging


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["uaecsd.com"]

    def start_requests(self) -> Iterator[Request]:
        BASE = 'https://uaecsd.com/_drts/entity/directory__listing/query/uae_contract_dir_ltg/'
        ua = FakeUserAgent()

        for letter in list('abcdefghijklmnopqrstuvwxyz'):
            params = urlencode({
                '_type_': 'json',
                'no_url': '0',
                'num': '200',
                'query': letter
            })
            yield Request(
                url=f'{BASE}?{params}',
                headers={
                    'User-Agent': ua.random
                },
                callback=self.parse_links
            )

    def parse_links(self, res: Response):

        response: list = json.loads(res.text)
        ua = FakeUserAgent()

        for link in response:
            logging.info(link)
            yield Request(
                url=link['url'],
                headers={
                    'User=Agent': ua.random
                }
            )

    def parse(self, res: Response):
        response: scrapy.Selector = res

        selector = 'div[data-name="entity_field_post_title"]::text'
        title = response.css(selector).get()

        category = response\
            .css('a[data-content-type="directory_category"]::text')\
            .get()

        address = response\
            .css('span.drts-location-address::text')\
            .get()

        phones = response\
            .css('a[data-phone-number]::attr(data-phone-number)')\
            .getall()

        website = response\
            .css('div[data-name="entity_field_field_website"] a::attr(href)')\
            .get()

        email = response\
            .css('div[data-name="entity_field_field_email"] a::attr(href)')\
            .get()

        yield {
            'title': title,
            'category': category,
            'address': address,
            'phones': phones,
            'website': website,
            'email': email
        }
