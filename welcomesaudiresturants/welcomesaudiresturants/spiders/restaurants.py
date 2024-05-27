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


class ResturantsSpider(scrapy.Spider):
    name = "restaurants"
    allowed_domains = ["welcomesaudi.com"]
    start_urls = [""]

    def start_requests(self) -> Iterable[Request]:
         BASE = "https://welcomesaudi.com/ar/restaurant?search=&restaurant_id="
         request = Request(url=BASE, callback=self.parse)
         request.meta['dont_cache'] = True
         return [request]


    def parse(self, res: Response):
        response: scrapy.Selector = res
        
        links = response.css('.item-title a::attr(href)').getall()
        for link in links:
             request = res.follow(
                  url=link,
                  callback=self.parse_restaurant
             )
             yield request

        next_page = response.css('a[rel="next"]::attr(href)').get('')
        if next_page:
             request = res.follow(
                  url=next_page,
                  callback=self.parse
             )
             request.meta['dont_cache'] = True
             yield request

    def parse_restaurant(self, res: Response):
        response: scrapy.Selector = res

        name = response.css('h1.h2::text').get('').strip()
        category = ''.join(response.css('.cuisines::text').getall()).strip()
        location = response.css('.location-title .address::text').get('')
        social_links = (
             response
             .css('.premium-feature-box .item::attr(href)')
             .getall()
        )
        telephone = response.xpath('//div/a[text()="اتصل بنا"]/@href').extract_first()
        rate = response.css('.rate i::text').get('')
        working_hours_el = response.css('.workinghours ul li')
        working_hours: dict = {}
        for hour in working_hours_el:
             day = hour.css('span:first-child::text').get('').strip()
             time = hour.css('span:last-child::text').get('').strip()
             working_hours[day] = time

        description: str = "\n".join(response.css('.description p::text').getall())
        google_maps = response.xpath('//a[text()=" احصل على الاتجاهات"]/@href').extract_first()
        
        yield {
             'name': name,
             'category': category,
             'location': location,
             'social_links': social_links,
             'telephone': telephone,
             'rate': rate,
             'working_hours': working_hours,
             'description': description,
             'google_maps': google_maps,
             'url': res.url
        }