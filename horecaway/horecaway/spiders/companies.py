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
    allowed_domains = ["horecaway.com"]
    start_urls = ["https://horecaway.com/index.jsp"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css(".blooh-dd > a::attr(href)").getall()
        for link in links:
            yield res.follow(url=res.urljoin(link), callback=self.parse_category)

    def parse_category(self, res: Response):
        response: scrapy.Selector = res
        links = response.css(".ban-block")
        for link in links:
            url = link.css("a::attr(href)").get("")
            category = link.css("a::text").get("")
            request = res.follow(
                url=res.urljoin(url),
                callback=self.parse_companies,
                cb_kwargs={"category": category},
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_companies(self, res: Response, category: str):
        response: scrapy.Selector = res
        links = response.css("#myTable > tbody > tr a::attr(href)").getall()
        for link in links:
            yield res.follow(
                url=res.urljoin(link),
                callback=self.parse_company,
                cb_kwargs={"category": category},
            )

    def parse_company(self, res: Response, category: str):
        response: scrapy.Selector = res

        title: str = response.css(".title-company::text").get("")
        category: str = (
            category
            .strip()
            .split('(')[0]
            .strip()
        )

        data: dict[str, str] = {}
        keys: list[scrapy.Selector] = response.css(".signle-ul li")
        for key in keys:
            k = key.css("span::text").get('').strip()
            v = [i.strip() for i in key.css("*::text").getall() if i.strip()]
            v = "".join(v)
            clean_row = {k: v.replace(k, '').strip()}
            data = {**data, **clean_row}

        tags = response.css(".cat-aat-a li a::text").getall()
        tags = [tag.strip() for tag in tags]
        tags = ", ".join(tags)

        google_maps = response.css('#mapDiv a.google-maps-link::attr(href)').get('')

        yield {
            "title": title,
            "category": category,
            "tags": tags,
            "url": res.url,
            "google_maps": google_maps,
            **data
        }
