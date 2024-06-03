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
    allowed_domains = ["www.iata.org"]
    start_urls = ["https://www.iata.org/en/publications/directories/cargolink/directory/?search=&ordering=Alphabetical#searchForm"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        
        links = response.css('td a::attr(href)').getall()
        for link in links:
             yield res.follow(
                  url=res.urljoin(link),
                  callback=self.parse_company
             )

        next_page = (
             response
             .xpath('//a[text()="Next"]/@href')
             .extract_first('')
        )
        if next_page:
             yield res.follow(url=next_page, callback=self.parse)

    def parse_company(self, res: Response):
        response: scrapy.Selector = res
        
        company_type = (
             response
             .xpath('//th[contains(text(), "Company Type")]/../td/text()')
             .extract_first('')
             .strip()
        )
        email = (
              response
              .xpath('//th[contains(text(), "Email")]/../td/a/@href')
              .extract_first('')
              .replace('mailto:', '')
              .strip()
        )
        phone = (
             response
             .xpath('//th[contains(text(), "Phone")]/../td/text()')
             .extract_first('')
             .strip()
        )
        address = (
             response
             .xpath('//th[contains(text(), "Address")]/../td/text()')
             .extract_first('')
             .strip()
        )
        yield {
             'name': response.css('title::text').get(''),
             'company_type': company_type,
             'email': email,
             'phone': phone,
             'address': address,
             'url': res.url
        }