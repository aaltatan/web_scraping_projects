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
    allowed_domains = ["careoptions.sa"]
    start_urls = ["https://careoptions.sa/products?search="]

    def parse(self, res: Response):
        response: scrapy.Selector = res

        items = response.css('.product .title a::attr(href)').getall()
        for item in items:
            request = res.follow(
                    url=res.urljoin(item),
                    callback=self.parse_item
                    )
            # request.meta['dont_cache'] = True
            yield request


        next_page = response.css('.page-link.next::attr(href)').get()
        if next_page:
            request = res.follow(
                    url=next_page,
                    callback=self.parse
                    )
            request.meta['dont_cache'] = True
            yield request

    def parse_item(self, res: Response):
        response: scrapy.Selector = res

        script_container = (
             response
             .xpath('//script[@src="/js/zid-tracking/zid-tracking.min.js?v=1.0.15.32446cd"]/following-sibling::script/following-sibling::script/text()')
             .extract_first('')
        )
        data = (
             script_container
             .replace('\n        var productObj = ', '')
             .replace(';\n        zidTracking.sendGaProductDetailViewedEvent({product: productObj});\n', '')
             .strip()
        )
        yield {
             **json.loads(data)
        }
