from scrapy.http import Request, Response
from fake_useragent import FakeUserAgent
import logging
import scrapy
import json


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class DevicesSpider(scrapy.Spider):
    name = "devices"
    allowed_domains = ["emma.sourcecode-ai.com"]
    start_urls = ["https://emma.sourcecode-ai.com/api/category"]
    ua = FakeUserAgent()

    def parse(self, res: Response):
        response: dict = json.loads(res.text)
        categories: list[dict] = response.get('productsCategories')
        for cat in categories:
            types: list[str] = ['mobile', 'accessories', 'tab']
            id: int = cat.get('id')
            name: str = cat.get('name')
            for t in types:
                yield Request(
                    url=f'https://emma.sourcecode-ai.com/api/products/{t}/{id}',
                    cb_kwargs={'category': name, 'type': t},
                    callback=self.parse_products
                )

    def parse_products(self, res: Response, category: str, type: str):
        response: dict = json.loads(res.text)
        products = response.get('products')
        for product in products:
            product['category'] = category
            product['type'] = type
            yield product