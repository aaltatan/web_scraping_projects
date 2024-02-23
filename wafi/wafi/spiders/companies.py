from scrapy.http import Request, Response, FormRequest
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

class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["wafi.housing.gov.sa"]
    start_urls = ["https://wafi.housing.gov.sa/passing-courses"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        rows = response.css('tbody tr')
        for row in rows:
            _, name, city, phone, email = row.css('td *::text').getall()[:5]
            yield {
                'name': name,
                'city': city,
                'phone': phone,
                'email': email,
            }
        
