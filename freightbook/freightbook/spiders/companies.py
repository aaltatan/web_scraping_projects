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


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.freightbook.net"]
    start_urls = ["https://www.freightbook.net/agent/search-results"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        
        cards = response.css('.business-card')
        links = response.css('.link_row')

        for card, link in zip(cards, links):
             yield {
                  'name': card.css('h2::text').get(''),
                  'country': card.css('.country-name::text').get(),
                  'address': card.css('.street-address::text').get(''),
                  'phones': card.css('.tel .value::text').getall(),
                  'email': link.css('a[href^="mailto:"]::attr(href)').get(),
                  'website': link.css('div:nth-child(3) a::attr(href)').get(),
             }
