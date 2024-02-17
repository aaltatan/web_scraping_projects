from typing import Iterator
import scrapy
from scrapy.http import Request, Response
import logging
import json
from fake_useragent import FakeUserAgent


logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.nab3.info"]
    ua = FakeUserAgent()

    def start_requests(self) -> Iterator[Request]:
        BASE = 'https://www.nab3.info/web.php'
        for page in range(1, int(self.end) + 1):
            params = f"page={page}&country=all&categories=all&degree=all"
            yield Request(url=f'{BASE}?{params}',
                          headers={'User-Agent': self.ua.random})

    def parse(self, res: Response):
        yield from json.loads(res.text)
