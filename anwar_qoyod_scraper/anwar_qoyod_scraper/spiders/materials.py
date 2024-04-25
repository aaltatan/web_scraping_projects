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


class MaterialsSpider(scrapy.Spider):
    name = "materials"
    allowed_domains = ["www.qoyod.com"]
    start_urls = ["https://www.qoyod.com/tenant/products?reset=true"]
    custom_cookies: dict = {
        "nitroCachedPage": "1",
        "pll_language": "ara",
        "pys_session_limit": "true",
        "pys_start_session": "true",
        "pys_first_visit": "true",
        "pysTrafficSource": "google.com",
        "pys_landing_page": "https://www.qoyod.com/",
        "last_pysTrafficSource": "google.com",
        "last_pys_landing_page": "https://www.qoyod.com/",
        "_fbp": "fb.1.1714029209494.7443521376",
        "intercom-id-nwliwnxy": "c1ef2414-784a-45b7-ad10-f4783f9e9d93",
        "intercom-device-id-nwliwnxy": "9867f1f9-8905-4a2f-ab05-d0a782207d73",
        "pbid": "e2a22a963eaefc59869175ba8ebc7416ba58fcaf49084fe7b915cc5e1bc12cf5",
        "_session_id": "f8d2186d6154c83c7852a2cacb2e6e5a",
        "intercom-session-nwliwnxy": "TWZ3RGk1MlZiMHBUc2RSZ3p5V2poQjd5YWx3cWcvbTdnY2FjN0JTZTF3YUxmRkpkWFFCS0Fxd2pFYTZ1VEx0SS0tZWJTam5nSmZKVU12TUZsajVVcWNJUT09--9e4428919a28b1d1cfb14d4b8634f62c89201cb",
    }
    ua = FakeUserAgent()

    def start_requests(self) -> Iterator[Request]:
        BASE = "https://www.qoyod.com/tenant/products?reset=true"
        requests_list: list = []
        for i in range(1, 50):
            url = BASE + f"&page={i}"
            request = Request(
                url=url,
                cookies=self.custom_cookies,
                headers={"User-Agent": self.ua.chrome},
            )
            requests_list.append(request)
        return requests_list

    def parse(self, res: Response):
        response: scrapy.Selector = res

        links = response.css('a[title="تعديل"]::attr(href)').getall()

        for link in links:
            yield res.follow(
                url=res.urljoin(link),
                headers={"User-Agent": self.ua.chrome},
                cookies=self.custom_cookies,
                callback=self.parse_material,
            )

    def parse_material(self, res: Response):
        response: scrapy.Selector = res

        name = response.css("#product_name::attr(value)").get("")
        sku = response.css("#product_sku::attr(value)").get("")
        price = response.css("#product_selling_price::attr(value)").get("")

        units: dict = {}

        table_row = response.css('#unit_conversions > tr')

        if table_row:
            for idx, tr in enumerate(table_row):

                unit: dict = {}

                name_id = '#product_unit_conversions_attributes_{}_from_unit option[selected]::text'
                rate_id = '#product_unit_conversions_attributes_{}_rate::attr(value)'
                price_id = '#product_unit_conversions_attributes_{}_unit_selling_price::attr(value)'

                unit_name =  tr.css(name_id.format(idx)).get()
                unit_rate =  tr.css(rate_id.format(idx)).get()
                unit_price = tr.css(price_id.format(idx)).get()

                unit['unit_name'] = unit_name
                unit['unit_rate'] = unit_rate
                unit['unit_price'] = unit_price

                units[idx] = unit


        yield {
            "name": name, 
            "sku": sku,
            "price": price,
            "units": units,
        }
