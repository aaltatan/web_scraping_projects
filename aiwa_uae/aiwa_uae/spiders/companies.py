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
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r)
                    for i in range(2, len(encodedString), 2)])
    return email


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["aiwa.ae"]
    custom_headers = {
        "Accept": "*/*",
        "Content-Type": "application/json" 
    }

    def start_requests(self) -> list[Request]:
        BASE = "https://aiwa.ae/api/services/app/industry/GetFeaturedIndustriesAsync"
        return [Request(url=BASE, method='POST')]

    def parse(self, res: Response):
        BASE = 'https://aiwa.ae/api/services/app/search/GetSearchResults'
        response: dict = json.loads(res.text)
        items: list[dict] = response.get('result').get('items')
        for item in items:
            item = item.get('keyword').lower()
            body = {
                "query": item,
                "sortByField": "relevance",
                "params": "origin_region=undefined",
                "pageIndex": 1,
                "pageSize": 1
            }
            yield res.follow(
                method='POST',
                url=BASE,
                body=json.dumps(body),
                callback=self.parse_companies,
                cb_kwargs={'item': item, 'url': BASE},
                headers=self.custom_headers
            )

    def parse_companies(self, res: Response, item: str, url: str):
        response: dict = json.loads(res.text)
        total_count: int = response['result']['result']['totalCount']
        step = int(self.step)
        for idx in range(1, (total_count + 1) // step):
            body = {
                "query": item,
                "sortByField": "relevance",
                "params": "origin_region=undefined",
                "pageIndex": idx,
                "pageSize": step
            }
            yield res.follow(
                method='POST',
                url=url,
                body=json.dumps(body),
                callback=self.parse_company,
                headers=self.custom_headers
            )

    def parse_company(self, res: Response):
        response: dict = json.loads(res.text)
        items: list[dict] = response['result']['result']['items']
        for item in items:
            yield item
