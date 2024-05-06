from scrapy.http import Request, Response, FormRequest
from urllib.parse import urlencode, parse_qs
from fake_useragent import FakeUserAgent
from typing import Iterator, Iterable
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


class FactoriesSpider(scrapy.Spider):
    name = "factories"
    allowed_domains = ["ausanticaret.com"]
    ua = FakeUserAgent()

    def start_requests(self) -> Iterable[Request]:
        BASE = "https://ausanticaret.com/wp-json/wiloke/v2/listings"

        end = int(getattr(self, 'end')) or 40

        requests: list[Request] = []

        for i in range(1, end):
            params = {
                "postType": "factories",
                "postsPerPage": '12',
                "offset": i,
                "pageNow": "search",
                "sc": "wil-async-grid",
            }
            params = urlencode(params)
            request = Request(
                url=BASE + '?' + params,
                headers={
                    'User-Agent': self.ua.random
                }
            )
            request.meta['dont_cache'] = True
            requests.append(request)

        return requests

    def parse(self, res: Response):
        response: dict = json.loads(res.text)
        factories: list[dict] = response['listings']
        for fact in factories:
            link = fact.get('permalink')
            yield Request(
                url=link,
                headers={
                    'User-Agent': self.ua.random
                },
                callback=self.parse_factory
            )
        

    def parse_factory(self, res: Response):
        response: scrapy.Selector = res

        name = (
            response
            .css('h1[class^="listing-detail_title"] > span::text')
            .get('')
            .strip()
        )
        description = (
            "\n".join(
                response
                .xpath('//h2//span[text()="وصف"]/../../../../div//p/text()')
                .extract()
            )
        )
        products = (
            ", ".join(
                response
                .css('.products h2::text')
                .getall()
            )
        )
        email = (
            response
            .css('.wil-listing-email a::attr(href)')
            .get('')
            .replace('mailto:', '')
        )
        phone = (
            response
            .css('.wil-listing-phone a::attr(href)')
            .get('')
            .replace('tel:', '')
        )
        website = (
            response
            .css('.wil-listing-website a::attr(href)')
            .get('')
        )
        address = (
            response
            .css('.wil-wrapper-text-field::text')
            .get()
        )
        category = response.xpath('//div/a[@title]//text()').extract_first()

        yield {
            'name': name,
            'description': description,
            'products': products,
            'email': email,
            'phone': phone,
            'website': website,
            'address': address,
            'category': category,
            'link': res.url
        }
