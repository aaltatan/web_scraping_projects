from scrapy.http import Request, Response, FormRequest
from fake_useragent import FakeUserAgent
from typing import Iterator, Iterable
import requests
import chompjs
import scrapy
import json
import re
import logging


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
    allowed_domains = ["bifa.org"]
    ua = FakeUserAgent()

    def start_requests(self) -> list[Request]:
        base = "https://bifa.org/membership/member-search/search-results/?address%5B0%5D=69%20Horse%20Guards%20Rd%2C%20London%20SW1A%202BJ%2C%20UK&post%5B0%5D=members&tax%5Bmembers_regions%5D%5B0%5D&tax%5Bmembers_specialisations%5D%5B0%5D&tax%5Bmembers_category%5D%5B0%5D=28&distance&units=imperial&per_page=25&lat=51.503013&lng=-0.130090&country&form=1&action=fs"

        headers = {
            'User-Agent': self.ua.random
        }

        request = Request(base, headers=headers)
        return [request]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        
        posts = response.css('li.single-post')

        for post in posts:
            yield {
                'title': post.css('.wppl-h2 a::text').get('').strip(),
                'link': post.css('.wppl-h2 a::attr(href)').get('').strip(),
                'distance': post.css('.wppl-h2 span.distance::text').get('').strip(),
                'website': post.css('.website span.info a::attr(href)').get('').strip(),
                'phone': post.css('.phone span.info a::text').get('').strip(),
                'address': post.css('.gmw-item-address a::text').get('').strip(),
                'google_maps': post.css('.gmw-item-address a::attr(href)').get('').strip(),
            }

        if response.css('.next'):
            next_page = response.css('a.next::attr(href)').get('')
            headers = {
                'User-Agent': self.ua.random
            }
            yield res.follow(url=next_page, callback=self.parse, headers=headers)


