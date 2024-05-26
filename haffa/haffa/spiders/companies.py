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
    allowed_domains = ["www.haffa.com.hk"]
    start_urls = ["https://www.haffa.com.hk/portal/Member/Default.aspx"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        
        links = response.css('.itemh::attr(href)').getall()
        for link in links:
             yield res.follow(
                  url=link,
                  callback=self.parse_email,
                  cb_kwargs={'website': link},
                  dont_filter=True
             )

    def parse_email(self, res: Response, website:str):
        response: scrapy.Selector = res
        emails = response.xpath('string(//body)').re('[A-z].+\@.+\..+')
        yield {
             'website': website,
             'emails': emails
        }

