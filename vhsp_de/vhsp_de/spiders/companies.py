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
    allowed_domains = ["www.vhsp.de"]
    start_urls = ["https://www.vhsp.de/mitglieder/"]

    def parse(self, res: Response):
        response: scrapy.Selector = res.copy()
        
        links = response.xpath('//script').re(r'\/\/www\.vhsp\.de\/vhsp\/firmenprofil\/\?mitglied\=\d+')
        for link in links:
            yield res.follow(
                url=link,
                callback=self.parse_company
            )

    def parse_company(self, res: Response):
        response: scrapy.Selector = res.copy()

        name = response.css('.firmenname h1::text').get('')
        address = response.css('.left .address::text').get('')
        plz = response.css('.left .plz::text').get('')
        city = response.css('.left .city::text').get('')

        data: dict = {}

        table_rows = response.css('.left table tr')
        for row in table_rows:
            k = row.css('tr td:first-child *::text').get('').strip().replace(':', '')
            v = row.css('tr td:last-child *::text').get()
            data[k] = v

        yield {
            'name': name,
            'address': address,
            'plz': plz,
            'city': city,
            **data,
            'url': res.url,
        }