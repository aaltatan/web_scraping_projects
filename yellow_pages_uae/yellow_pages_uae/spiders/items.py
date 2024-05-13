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


logging.basicConfig(
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class ItemsSpider(scrapy.Spider):
    name = "items"
    allowed_domains = ["www.yellowpages.ae"]
    ua = FakeUserAgent()

    def start_requests(self) -> list[Request]:
        BASE = "https://www.yellowpages.ae/category"
        request = Request(BASE)
        request.meta['dont_cache'] = True
        return [request]

    def parse_response_func(self, response: Response) -> dict:
        script: str = (
            response
            .css('script[type="application/json"]::text')
            .get()
        )
        script = script.replace('&q;', '"')
        return chompjs.parse_js_object(script)

    def generate_links_func(self, categories: list) -> list:
        links = []
        for category in categories:
            name: str = category['categoryName']
            name = (
                name
                .strip()
                .replace('&a;', '&')
                .replace(' ', '-')
                .lower()
            )
            BASE = "https://www.yellowpages.ae/category"
            link = BASE + "/" + name + '/' + category['id']
            links.append(link)
        return links

    def parse(self, response: Response):
        data = self.parse_response_func(response)
        categories = data['G.https://api.yellowpages.ae/api/guest/products-categories-min?page=0&a;size=10000']['body']
        links = self.generate_links_func(categories)
        for link in links:
            request = response.follow(link, self.parse_subcategory)
            request.meta['dont_cache'] = True
            yield request

    def parse_subcategory(self, response: Response):
        data = self.parse_response_func(response)
        key = list(data.keys())[0]
        subcategories = [sub['subCategoryName'].replace(
            '&a;', '&').lower() for sub in data[key]['productsSubcategories']]

        endpoint = 'https://api.yellowpages.ae/api/new-search-products'
        headers = {
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json'
        }

        for subcategory in subcategories:
            request = Request(
                url=f'{endpoint}?{urlencode({'page': 0, 'size': 1_000})}',
                method='POST',
                callback=self.parse_product,
                headers=headers,
                dont_filter=True,
                body=json.dumps({
                    'searchText': subcategory,
                    'searchTypeText': 'subcategory'
                }),
            )
            request.meta['dont_cache'] = True
            yield request

    def parse_product(self, response: Response):
        yield from json.loads(response.text)['products']
