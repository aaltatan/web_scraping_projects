from scrapy.http import Request, Response, FormRequest
from urllib.parse import urlencode, parse_qs
from fake_useragent import FakeUserAgent
from typing import Iterator, Iterable
import requests
import logging
import chompjs
import scrapy
import math
import json
import re


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


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.europages.ma"]
    start_urls = ["https://www.europages.ma/bs"]
    base = "https://www.europages.ma/ep-api/v2/serp/companies"

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('div[role="list"] a::attr(href)').getall()[1:]
        categories = response.css('div[role="list"] a::text').getall()[1:]
        for link, category in zip(links, categories):
            request = res.follow(
                url=res.urljoin(link),
                callback=self.parse_category,
                cb_kwargs={"category": category},
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_category(self, res: Response, category: str):
        response: scrapy.Selector = res

        links = response.css('div[role="list"] a::text').getall()[1:]
        for link in links:
            query = {
                "lang": "ar",
                "search": link,
                "page": "1",
                "mode": "default",
            }
            request = Request(
                url=self.base + "?" + urlencode(query=query),
                callback=self.parse_subcategory,
                cb_kwargs={"link": link, "category": category, "subcategory": link},
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_subcategory(
        self,
        res: Response,
        link: str,
        category: str,
        subcategory: str,
    ):
        response: dict = json.loads(res.text)

        items_per_page: int = response["meta"]["itemsPerPage"]
        total_items: int = response["meta"]["totalItems"]
        pages_count = math.ceil(total_items / items_per_page)

        for page in range(1, pages_count + 1):
            query = {
                "lang": "ar",
                "search": link,
                "page": str(page),
                "mode": "default",
            }
            request = Request(
                url=self.base + "?" + urlencode(query=query),
                callback=self.parse_id,
                cb_kwargs={
                    "category": category,
                    "subcategory": subcategory,
                },
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_id(
        self,
        res: Response,
        category: str,
        subcategory: str,
    ):
        response: dict = json.loads(res.text)
        items_ids: list[str] = [item["id"] for item in response["items"]]
        for id in items_ids:
            yield Request(
                url=f"https://www.europages.ma/ep-api/v2/epages/{id}?lang=ar",
                callback=self.parse_url,
                cb_kwargs={
                    "category": category,
                    "subcategory": subcategory,
                },
            )

    def parse_url(
        self,
        res: Response,
        category: str,
        subcategory: str,
    ):
        response: dict = json.loads(res.text)
        response = {"category": category, "subcategory": subcategory, **response}
        id: str = response["id"]
        yield Request(
            url=f"https://www.europages.ma/ep-api/v2/epages/{id}/phones",
            callback=self.parse_phone,
            cb_kwargs={
                "data": response,
            },
        )

    def parse_phone(self, res: Response, data: dict):
        response: dict = json.loads(res.text)
        phones = response["phones"]
        yield {
            "phones": phones,
            **data,
        }

    # def parse_item(self, res: Response):
    #     response: scrapy.Selector = res
    #     func: str = response.css('script::text')[-1].get()
    #     data_str = func.split('return ')[-1]
    #     data = chompjs.parse_js_object(data_str)

    #     yield {
    #         **data
    #     }
