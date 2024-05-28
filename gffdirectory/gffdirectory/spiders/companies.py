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
    allowed_domains = ["search.gffdirectory.com"]
    start_urls = ["https://search.gffdirectory.com/"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        
        cards = response.css('.isotope-item')
        for card in cards:
             data =  [i.strip() for i in 
                      card.css('.thumb-info-content::text').getall()]
             yield {
                  'data': data,
             }

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
             yield res.follow(url=next_page, callback=self.parse)