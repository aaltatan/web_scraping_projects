import scrapy
from typing import Iterator
import json
from scrapy.http import Request, Response, FormRequest
import logging
import re
import requests

logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)

def generate_formdata(start: int, length: int) -> dict:
    return {
            'draw': '2',
            'columns%5B0%5D%5Bdata%5D': 'LogoUrl',
            'columns%5B0%5D%5Bname%5D': '',
            'columns%5B0%5D%5Bsearchable%5D': 'true',
            'columns%5B0%5D%5Borderable%5D': 'false',
            'columns%5B0%5D%5Bsearch%5D%5Bvalue%5D': '',
            'columns%5B0%5D%5Bsearch%5D%5Bregex%5D': 'false',
            'columns%5B1%5D%5Bdata%5D': 'OfficeId',
            'columns%5B1%5D%5Bname%5D': '',
            'columns%5B1%5D%5Bsearchable%5D': 'true',
            'columns%5B1%5D%5Borderable%5D': 'true',
            'columns%5B1%5D%5Bsearch%5D%5Bvalue%5D': '',
            'columns%5B1%5D%5Bsearch%5D%5Bregex%5D': 'false',
            'columns%5B2%5D%5Bdata%5D': 'OfficeName',
            'columns%5B2%5D%5Bname%5D': '',
            'columns%5B2%5D%5Bsearchable%5D': 'true',
            'columns%5B2%5D%5Borderable%5D': 'true',
            'columns%5B2%5D%5Bsearch%5D%5Bvalue%5D': '',
            'columns%5B2%5D%5Bsearch%5D%5Bregex%5D': 'false',
            'columns%5B3%5D%5Bdata%5D': 'MobileNo',
            'columns%5B3%5D%5Bname%5D': '',
            'columns%5B3%5D%5Bsearchable%5D': 'true',
            'columns%5B3%5D%5Borderable%5D': 'true',
            'columns%5B3%5D%5Bsearch%5D%5Bvalue%5D': '',
            'columns%5B3%5D%5Bsearch%5D%5Bregex%5D': 'false',
            'columns%5B4%5D%5Bdata%5D': 'ClassificationGrade',
            'columns%5B4%5D%5Bname%5D': '',
            'columns%5B4%5D%5Bsearchable%5D': 'true',
            'columns%5B4%5D%5Borderable%5D': 'true',
            'columns%5B4%5D%5Bsearch%5D%5Bvalue%5D': '',
            'columns%5B4%5D%5Bsearch%5D%5Bregex%5D': 'false',
            'columns%5B5%5D%5Bdata%5D': 'OfficeId',
            'columns%5B5%5D%5Bname%5D': '',
            'columns%5B5%5D%5Bsearchable%5D': 'true',
            'columns%5B5%5D%5Borderable%5D': 'false',
            'columns%5B5%5D%5Bsearch%5D%5Bvalue%5D': '',
            'columns%5B5%5D%5Bsearch%5D%5Bregex%5D': 'false',
            'start': str(start),
            'length': str(length),
            'search%5Bvalue%5D': '',
            'search%5Bregex%5D': 'false',
            'regionId': '-1',
            'cityId': '-1',
            'textSearch': '',
            'activity': '' 
        }

class BaladySpider(scrapy.Spider):
    name = "balady"
    allowed_domains = ["apps.balady.gov.sa"]

    # ? scrapy crawl balady -a step=100

    def start_requests(self) -> Iterator[FormRequest]:
        BASE = "https://apps.balady.gov.sa/Eservices/Inquiries/InquiryEngOffices/LoadData"

        payload = generate_formdata(0, 100)
        try:
            response = requests.post(BASE, data=payload)
            response_data: dict = response.json()
            end = response_data.get('recordsFiltered')
        except:
            end = 4_583

        length = int(self.step)

        for idx in range(0, end, length):
            formdata = generate_formdata(idx, length)
            request = FormRequest(url=BASE, formdata=formdata)
            request.meta['dont_cache'] = True
            yield request

    def parse(self, res: Response):
        response: dict = json.loads(res.text)
        data: list = response.get('data')
        for office in data:
            BASE = 'https://apps.balady.gov.sa/Eservices/Inquiries/InquiryEngOffices/Details'
            office_id = office.get('OfficeId')
            yield Request(
                url=f'{BASE}?OfficeId={office_id}',
                callback=self.parse_office
            )

    def parse_office(self, res: Response):
        response: scrapy.Selector = res

        data: dict = {}

        regex = re.compile(r'\s{2,}')

        details = response.css('.item-content-details')
        for detail in details:
            key = (
                detail
                .css('.title::text')
                .get()
                .strip()
            )
            value = ''
            if detail.css('.description::text'):
                value = (
                    detail
                    .css('.description::text')
                    .get()
                    .strip()
                )
                value = regex.sub('', value)
            data[key] = value

        yield {
            **data,
            'url': res.url
        }

