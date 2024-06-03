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


class ItemsSpider(scrapy.Spider):
    name = "items"
    allowed_domains = ["knooz-store.com"]
    ua = FakeUserAgent()
    def start_requests(self) -> Iterable[Request]:
         BASE = "https://knooz-store.com/api/v1/products?page="
         end = getattr(self, 'end', 244)

         request_list: list = []

         for i in range(1, end + 1):
              req = Request(
                   url=BASE + str(i),
                   headers={
                        'User-Agent': self.ua.random
                   }
              )
              req.meta['dont_cache'] = True
              request_list.append(req)

         return request_list


    def parse(self, res: Response):

        print(res.text)

        response: dict = json.loads(res.text)
        products = response['data']['products']['data']
        for product in products:
            yield {**product}
