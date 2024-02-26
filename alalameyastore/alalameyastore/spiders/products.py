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
from ..items import ProductItem


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


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["alalameyastore.com"]
    start_urls = ["https://alalameyastore.com/?s=&product_cat=0&post_type=product&lang=ar"]

    def parse(self, res :Response):
        response: scrapy.Selector = res
        links = response.css('a.woocommerce-loop-product__link::attr(href)').getall()
        print(links)
        print("#" * 50)
        links = list(set(links))
        for link in links:
             yield res.follow(url=link, callback=self.parse_page)

        next_page = (
              response
              .xpath('//*[@class="woocommerce-pagination"]//a[text()="←"]/@href')
              .extract_first('')
        )
        if next_page:
             yield res.follow(url=next_page, callback=self.parse)

    def parse_page(self, res: Response):
        response: scrapy.Selector = res

        item = ProductItem()

        item['title'] = response.css('title::text').get(''),
        item['image_urls'] = response.css('.woocommerce-product-gallery__image a::attr(href)').getall()

        yield item


