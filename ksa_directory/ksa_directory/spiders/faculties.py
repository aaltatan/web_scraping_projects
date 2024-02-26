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


class FacultiesSpider(scrapy.Spider):
    name = "faculties"
    allowed_domains = ["www.ksa.directory"]

    def start_requests(self) -> list[Request]:
        request = Request("https://www.ksa.directory/search")
        request.meta['dont_cache'] = True
        return [request]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('.txt > a::attr(href)').getall()
        for link in links:
            logging.info(res.urljoin(link))
            yield res.follow(url=res.urljoin(link),
                             callback=self.parse_page)

        next_page = (
            response
            .xpath('//span[text()="Next"]/../@href')
            .extract_first('')
        )
        if next_page != "#":
            request = res.follow(url=next_page,
                                 callback=self.parse)
            request.meta['dont_cache'] = True
            yield request

    def parse_page(self, res: Response):
        response: scrapy.Selector = res
        title = (
            response
            .xpath('//h1[@itemprop="name"]/text()')
            .extract_first('')
        )
        departments = (
            response
            .xpath('//span[@itemprop="department"]/text()')
            .extract()
        )
        location = (
            response
            .xpath('//*[@itemprop="location"]/text()')
            .extract_first('')
        )
        telephone = (
            response
            .xpath('//*[@itemprop="telephone"]/../@href')
            .extract_first('')
        )
        if telephone:
            telephone = telephone.split(':')[-1]
        email = (
            response
            .xpath('//*[@itemprop="email"]/span/@data-cfemail')
            .extract_first('')
        )
        if email:
            email = cf_decode_email(email)
        url = (
            response
            .xpath('//*[@itemprop="url"]/@href')
            .extract_first('')
        )

        socials = response.css('.listing-social a')
        if socials:
            socials = {
                s.css('a::attr(class)').get('').strip():
                s.css('a::attr(href)').get('')
                for s in socials
            }
        else:
            socials = dict()

        yield {
            'title': title,
            'departments': departments,
            'location': location,
            'telephone': telephone,
            'email': email,
            'url': url,
            'link': res.url,
            **socials
        }
