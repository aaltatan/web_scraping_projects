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

COOKIES = {
    'mailchimp.cart.current_email': 'a.altatan@gmail.com',
    'woocommerce_multicurrency_forced_currency': 'GBP',
    'woocommerce_multicurrency_language': 'en',
    'wordpress_logged_in_4433e76b79f68b892e96df1104f86865': 'a.altatan%7C1732530264%7C0Ezltnly91vOL41C5mup6I9PG31lFWTyVtboO7kbOqb%7C0517fd51e4ffef6407d9f5f6f0842ac4b58d38a5467ceb595641e4cdf44385f4',
    'az_co': 'tr',
    'sbjs_migrations': '1418474375998%3D1',
    'sbjs_current_add': 'fd%3D2024-05-26%2019%3A30%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fazfreight.com%2Fmy-account%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fazfreight.com%2Fmy-account%2F',
    'sbjs_first_add': 'fd%3D2024-05-26%2019%3A30%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fazfreight.com%2Fmy-account%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fazfreight.com%2Fmy-account%2F',
    'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29',
    'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29',
    'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F125.0.0.0%20Safari%2F537.36',
    'cmplz_policy_id': '18',
    'cmplz_marketing': 'allow',
    'cmplz_statistics': 'allow',
    'cmplz_preferences': 'allow',
    'cmplz_functional': 'allow',
    'cmplz_banner-status': 'dismissed',
    'mailchimp_landing_site': 'https%3A%2F%2Fazfreight.com%2Fdirectory%2F',
    'sbjs_session': 'pgs%3D17%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fazfreight.com%2Faviation-service%2Fshanghai-waycan-industrial-co-ltd%2F'
}


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
    allowed_domains = ["azfreight.com"]
    start_urls = ["https://azfreight.com/directory/"]

    def parse(self, res: Response):

        response: scrapy.Selector = res
        BASE = "https://azfreight.com/wp-content/plugins/azfreight/directory.php"

        facilities = (
            response
            .css("#facSelect option::attr(value)")
            .getall()[8:]
        )
        countries_short = (
            response
            .css("#az_country_selected ~ ul > li > span::attr(data-val)")
            .getall()
        )
        countries_names = (
            response
            .css("#az_country_selected ~ ul > li > span:last-child::text")
            .getall()
        )
        countries_names = [c.strip() for c in countries_names]
        countries = zip(countries_short, countries_names)
        for facility in facilities:
            for country in countries:
                data: dict[str, str] = {
                    "action": "search_twenty_one",
                    "co": country[0],
                    "fac": facility,
                }
                query = urlencode(data)
                request = res.follow(
                    url=BASE + "?" + query,
                    callback=self.parse_ajax,
                    cb_kwargs={"country": country[-1], "facility": facility},
                    dont_filter=True,
                )
                request.meta["dont_cache"] = True
                yield request

    def parse_ajax(self, res: Response, country: str, facility: str):
        response: scrapy.Selector = res
        links = response.css('.link_button a[target="_blank"]::attr(href)').getall()
        for link in links:
            yield res.follow(
                url=link,
                callback=self.parse_company,
                cb_kwargs={"country": country, "facility": facility},
                cookies=COOKIES
            )

    def parse_company(self, res: Response, country: str, facility: str):
        response: scrapy.Selector = res
        yield {
            "title": response.css("title::text").get(""),
            "url": res.url,
            "country": country,
            "facility": facility,
        }
