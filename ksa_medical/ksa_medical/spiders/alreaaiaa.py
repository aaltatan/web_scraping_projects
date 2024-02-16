from typing import Iterator
import scrapy
from scrapy.http import Request, Response
from fake_useragent import FakeUserAgent
import json
import logging


logging.basicConfig(
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class AlreaaiaaSpider(scrapy.Spider):
    name = "alreaaiaa"
    allowed_domains = ["alreaaiaa.com"]
    ua = FakeUserAgent()

    def start_requests(self) -> Iterator[Request]:
        BASE = 'https://api.alreaaiaa.com/api/web_search_by_all/ar'

        for idx in range(1, 163):
            yield Request(
                url=BASE + f"?page={idx}",
                headers={
                    'User-Agent': self.ua.random,
                    'Content-Type': 'application/json'
                },
                method='POST',
                body=json.dumps({"country_id": 1})
            )

    def parse(self, res: Response):
        response: dict = json.loads(res.text)
        yield from response['data']
