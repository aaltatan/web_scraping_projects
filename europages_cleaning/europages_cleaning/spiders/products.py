from scrapy.http import Request, Response, FormRequest
from urllib.parse import urlencode, parse_qs
from fake_useragent import FakeUserAgent
from typing import Any, Iterator, Iterable
import requests
import logging
import chompjs
import scrapy
import json
import re
import math
from icecream import ic


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


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["www.europages.co.uk"]
    brands: list[str] = ["tide", "downy", "ariel", "vanish"]
    base = "https://www.europages.co.uk/ep-api/v2/serp/products"

    def start_requests(self) -> Iterable[Request]:
        reqs: list = []
        for brand in self.brands:
            query: dict[str, Any] = {
                "lang": "en",
                "search": brand,
                "page": "1",
                "mode": "default",
            }
            request = Request(
                url=self.base + "?" + urlencode(query),
                callback=self.parse,
                cb_kwargs={"brand": brand},
            )
            request.meta["dont_cache"] = True
            reqs.append(request)

        return reqs

    def parse(self, res: Response, brand: str):
        response: dict = json.loads(res.text)
        products = response.get("items", [])
        for product in products:
            id = product["epage"]["id"]
            product = {"brand": brand, **product}
            yield Request(
                url=f"https://www.europages.ma/ep-api/v2/epages/{id}/phones",
                callback=self.parse_phone,
                dont_filter=True,
                cb_kwargs={
                    "product": product,
                },
            )

    def parse_phone(self, res: Response, product: dict):
        response: dict = json.loads(res.text)
        ic(response)
        phones = response["phones"]
        phones = phones[0]['items'][0]['number']
        yield {
            "phones": phones,
            **product,
        }
