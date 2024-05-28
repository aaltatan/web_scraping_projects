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
    allowed_domains = ["fiata.org"]
    start_urls = ["https://fiata.org/directory/"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        countries = response.css("#country option::attr(value)").getall()[1:]
        countries_names = response.css("#country option::text").getall()[1:]
        BASE = "https://fiata.org/directory/"
        for c, name in zip(countries, countries_names):
            yield res.follow(
                url=BASE + c + "/",
                callback=self.parse_company,
                cb_kwargs={"country": name},
            )

    def parse_company(self, res: Response, country: str):
        response: scrapy.Selector = res
        cards = response.css("main section")

        website_xpath = \
              './/dl//dt[text()="website"]/following-sibling::dd/text()'
        telephone_xpath = \
              './/dl//dt[text()="tel."]/following-sibling::dd/text()'
        email_xpath = \
              './/dl//dt[text()="email"]/following-sibling::dd/a/@data-cfemail'

        for card in cards:

            website = card.xpath(website_xpath).extract_first('')
            telephone = card.xpath(telephone_xpath).extract_first('')

            enc_email = card.xpath(email_xpath).extract_first('')

            email = cf_decode_email(enc_email)

            name = card.css('h3::text').get('').strip()

            yield {
                'name': name,
                'telephone': telephone,
                'country': country,
                'website': website,
                'email': email,
                'url': res.url
            }

