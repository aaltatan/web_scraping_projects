from scrapy.http import Request, Response, FormRequest
from urllib.parse import urlencode, parse_qs
from fake_useragent import FakeUserAgent
from typing import Iterator, Iterable
import requests
import logging
import chompjs
import scrapy
import json
import re


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)

def cf_decode_email(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


class EntitiesSpider(scrapy.Spider):
    name = "entities"
    allowed_domains = ["es.ncnp.gov.sa"]
    start_urls = ["https://es.ncnp.gov.sa/v5/nonprofits?name=&number=&type=1"]

    def parse(self, res: Response):
        response: scrapy.Selector = res.copy()

        links = response.css('.card-title a:first-child::attr(href)').getall()
        for link in links:
            yield res.follow(
                url=link,
                callback=self.parse_entity
            )

        next_page = response.css('a[rel="next"]::attr(href)').get('')

        if next_page:
            yield res.follow(
                url=next_page,
                callback=self.parse
            )

    def parse_entity(self, res: Response):
        response: scrapy.Selector = res.copy()

        title = response.css('.main-info-details h5::text').get('').strip()
        tag = response.css('.light.tag::text').get('')
        description = response.css('.main-info-details p::text').getall()

        description = "\n".join([l.strip() for l in description])

        data: dict = {}

        lis = response.css('.main-info-details li')

        for li in lis[:-1]:

            key = li.css('a *::text').getall()
            key = [k.strip() for k in key if k.strip()][0]
            key = key.split(':')[0].strip()
            value = li.css('a::attr(href)').get('')

            if key == 'البريد الالكتروني':
                value = cf_decode_email(value.split("#")[-1])

            data[key] = value

        yield {
            'title': title,
            'tag': tag,
            'description': description,
            **data,
        }