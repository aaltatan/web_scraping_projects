from scrapy.http import Request, Response
from fake_useragent import FakeUserAgent
from dotenv import load_dotenv
from typing import Iterator
import requests
import logging
import scrapy
import json
import os

load_dotenv()

logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


def generate_params(skip: int, count: int) -> str:
    return f"sortBy=2&sortDirection=2&skipCount={skip}&maxResultCount={count}"


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["api.thiqah.sa"]
    ua = FakeUserAgent()
    custom_headers = {
        "User-Agent": ua.random,
        "Apikey": os.environ["API_KEY_MAROOF"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en",
    }

    def start_requests(self) -> Iterator[Request]:

        # ? scrapy crawl products -O .\data\new_data.jsonl -a step=10

        BASE = "https://api.thiqah.sa/maroof/public/api/app/business/search"

        start = 0
        step = int(self.step)

        try:
            params = generate_params(start, step)
            self.custom_headers["User-Agent"] = self.ua.random
            response = requests.get(url=f"{BASE}?{params}", headers=self.custom_headers)
            end = response.json()["totalCount"]
        except:
            end = 60_000

        for idx in range(start, end, step):
            params = generate_params(idx, step)
            self.custom_headers["User-Agent"] = self.ua.random
            request = Request(
                url=f"{BASE}?{params}",
                headers=self.custom_headers,
            )
            request.meta["dont_cache"] = True
            yield request

    def parse(self, res: Response):
        items = json.loads(res.text)["items"]
        for item in items:
            self.custom_headers["User-Agent"] = self.ua.random
            yield res.follow(
                url=f"https://api.thiqah.sa/maroof/public/api/app/business/"
                + str(item["id"]),
                headers=self.custom_headers,
                callback=self.parse_item,
            )

    def parse_item(self, res: Response):
        response_json = json.loads(res.text)
        yield response_json
