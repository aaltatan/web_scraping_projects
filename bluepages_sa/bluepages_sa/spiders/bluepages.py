from typing import Iterator
import scrapy
from scrapy.http import Request, Response
import requests
import json
import logging
from urllib.parse import urlencode

logging.basicConfig(
    filemode='a',
    filename='logger.log',
    encoding='utf-8',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)


class BluepagesSpider(scrapy.Spider):
    name = "bluepages"
    allowed_domains = ["bluepages.com.sa"]

    def start_requests(self) -> Iterator[Request]:
        BASE = 'https://bluepages.com.sa/api/companies/getAll/paginate'
        try:
            response: dict = requests.get(BASE).json()
            end = response['meta']['totalPages']
        except:
            end = 10160

        for idx in range(1, end+1):
            params = {'page': idx,
                      'city': "true",
                      'countryId': 1,
                      'freeCompanies': "true",
                      'status': "true"}
            params = urlencode(params)
            request = Request(url=f'{BASE}?{params}')
            request.meta['dont_cache']
            yield request

    def parse(self, res: Response):
        response: dict = json.loads(res.text)
        companies = response.get('items')
        yield from companies
