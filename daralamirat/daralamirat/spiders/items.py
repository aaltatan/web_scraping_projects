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


with open("./refs.txt", "r", encoding="utf-8") as file:
    refs = [ref[:-1] for ref in file.readlines()]

logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


def cf_decode_email(encodedString):
    r = int(encodedString[:2], 16)
    email = "".join(
        [
            chr(int(encodedString[i : i + 2], 16) ^ r)
            for i in range(2, len(encodedString), 2)
        ]
    )
    return email


class ItemsSpider(scrapy.Spider):
    name = "items"
    allowed_domains = ["daralamirat.com.sa"]
    start_urls = ["https://daralamirat.com.sa/"]

    def start_requests(self) -> Iterable[Request]:

        requests_list: list = []

        for ref in refs:

            href = ref.split('/')[-1][1:]

            BASE = f"https://api.salla.dev/store/v1/products?source=categories&source_value[]={href}"
            headers = {"Store-Identifier": "1945128061"}
            requests_list.append(Request(BASE, headers=headers, dont_filter=True))

        return requests_list

    def parse(self, res: Response):
        response: dict = json.loads(res.text)

        next_page: dict = response.get("cursor")
        if next_page:
            next_page = next_page.get("next")
            if next_page:
                yield Request(
                    url=next_page,
                    callback=self.parse,
                    headers={"Store-Identifier": "1945128061"},
                    dont_filter=True,
                )

        items: list[dict] = response.get("data")
        for item in items:
            yield {**item}
