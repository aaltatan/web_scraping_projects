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
    allowed_domains = ["www.haffa.com.hk"]
    start_urls = ["https://www.haffa.com.hk/portal/Member/Default.aspx"]

    def parse(self, res: Response):
        response: scrapy.Selector = res

        links = response.css(".itemh::attr(href)").getall()
        for link in links:
            yield res.follow(
                url=link,
                callback=self.parse_email_or_contact,
                cb_kwargs={"website": link},
                dont_filter=True,
            )

    def parse_email_or_contact(self, res: Response, website: str):
        response: scrapy.Selector = res
        emails = response.xpath("string(//body)").re(r"[\'\"\s][A-z].+\@.+\..+[\'\"\s]")
        json_emails = json.dumps(emails)
        links = response.xpath('//a[contains(@href, "/contact")]/@href').extract()
        links = list(set(links))
        for link in links:

            if link.startswith("/"):
                url = website + link
            else:
                url = link

            res.follow(
                url=url,
                callback=self.parse_emails,
                cb_kwargs={"emails_json": json_emails, "website": website},
            )

    def parse_emails(self, res: Response, emails_json: str, website: str):

        response: scrapy.Selector = res

        emails = json.loads(emails_json)
        new_emails = response.xpath("string(//body)").re(
            r"[\'\"\s][A-z].+\@.+\..+[\'\"\s]"
        )

        print(emails)
        print(new_emails)
        print("#" * 100)

        yield {"website": website, "emails": [*emails, *new_emails]}
