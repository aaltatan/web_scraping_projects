from typing import Iterable
import scrapy
from scrapy.http import Request, Response
import json
import logging
from fake_useragent import FakeUserAgent


logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)

class SakaniSpider(scrapy.Spider):
    name = "sakani"
    allowed_domains = ["sakani.sa"]
    ua = FakeUserAgent()

    def start_requests(self) -> Iterable[Request]:
        BASE = "https://sakani.sa/mainIntermediaryApi/v2/certified_engineering_offices"
        reqs = []
        for idx in range(1, 5):
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Referer': 'https://sakani.sa/app/certified-engineering-offices',
            }
            params = f'page[size]=500&page[number]={idx}'
            request = Request(url=f'{BASE}?{params}', headers=headers)
            reqs.append(request)
        return reqs

    def parse(self, res: Response):
        response: dict = json.loads(res.text)
        yield from response.get('data')
