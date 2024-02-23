from scrapy.http import Response, Request, FormRequest
from selectolax.parser import HTMLParser
from typing import Iterator
import requests
import logging
import scrapy
import json


logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="%(asctime)s %(levelname)s | %(name)s [%(message)s]",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    encoding="utf-8",
)


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["businssdirectory.com"]

    def start_requests(self) -> Iterator[FormRequest]:
        BASE = "https://businssdirectory.com/wp-admin/admin-ajax.php"

        pagination_url = 'https://businssdirectory.com/%D8%A7%D9%84%D9%86%D8%B4%D8%A7%D8%B7%D8%A7%D8%AA-%D8%A7%D9%84%D8%AA%D8%AC%D8%A7%D8%B1%D9%8A%D8%A9/'

        try:
            response = requests.get(pagination_url, timeout=90)
            parser = HTMLParser(response.text)
            pagination = parser.css('#listing_ajax_pagination li')
            end = max([int(li.attributes.get('data-page-no'))
                      for li in pagination])
        except:
            end = 14_921

        for page in range(1, end + 1):
            formdata = {"action": "dwt_ajax_search", "page_no": str(page)}
            request = FormRequest(url=BASE, formdata=formdata)
            request.meta["dont_cache"] = True
            yield request

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css("h2.group > a::attr(href)").getall()
        for link in links:
            yield Request(url=link, callback=self.parse_company)

    def parse_company(self, res: Response):
        response: scrapy.Selector = res
        category = response.css(".list-category a::text").get()
        title = response.css(".list-heading *::text").get()
        posted_at = response.css(".list-posted-date::text").get()
        s = "section.single-detail-page > .container > .row > div:first-child .panel-body p::text"
        description = response.css(s).get()

        contact_container = response.css("#tab1default")
        social_media = []
        if contact_container.css(".social-media a"):
            social_media = contact_container.css(
                ".social-media a::attr(href)").getall()

        address = ""

        if contact_container.css(".widget-listing-details > :not(li[class])"):
            address = contact_container.css(
                ".widget-listing-details > :not(li[class]) > h2 > span:nth-child(2) a::text"
            ).getall()
            address = ", ".join(address)

        website = ""
        if response.css('a[data-reaction="web"]'):
            website = response.css('a[data-reaction="web"]::attr(href)').get()

        data = {
            "title": title,
            "category": category,
            "posted_at": posted_at,
            "description": description,
            "social_media": social_media,
            "address": address,
            "website": website,
        }

        phone_id = ""
        if response.css("#listing-contact-phone"):
            phone_id = response.css(
                "#listing-contact-phone::attr(data-listing-id)"
            ).get()
            formdata = {
                'action': 'retreive_phone_number',
                'listing_id': phone_id
            }
            yield FormRequest(
                url='https://businssdirectory.com/wp-admin/admin-ajax.php',
                formdata=formdata,
                callback=self.parse_phone,
                cb_kwargs={'data': json.dumps(data)},
            )
        else:
            yield data

    def parse_phone(self, res: Response, data: str):
        response: dict = json.loads(res.text)
        data: dict = json.loads(data)

        phone = response.get('resp')
        data['phone'] = phone

        yield data
