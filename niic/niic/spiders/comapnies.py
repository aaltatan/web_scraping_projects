from typing import Iterator
import scrapy
from scrapy.http import Response, FormRequest, Request
import json
import logging

logging.basicConfig(
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["fd.niic.gov.sa"]

    # ? scrapy crawl companies -O data\data.jsonl -a end=11401

    def start_requests(self) -> Iterator[FormRequest]:
        BASE = 'https://fd.niic.gov.sa/Home/PlantList'
        for i in range(0, int(self.end) + 1, 20):
            yield FormRequest(
                url=BASE,
                formdata={'start': str(i)},
                dont_filter=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                }
            )

    def parse(self, res: Response):
        BASE = 'https://fd.niic.gov.sa/Home/GetPlantDetails'
        ids = [company.get('id')
               for company in json.loads(res.text).get('data')]
        for id in ids:
            yield Request(
                url=f'{BASE}?plantId={id}',
                callback=self.parse_item,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                }
            )

    def parse_item(self, res: Response):
        response: scrapy.Selector = res

        data = {}
        lis = response.css('ul li')
        for li in lis:
            key = li.css('.label::text').get()
            if key:
                key.strip()
            value = li.css('.value::text').get()
            if value:
                value.strip()
            data[key] = value

        selector = 'table tr td:first-child::text'
        materials = response.css(selector).getall()
        materials = "\n".join([m.strip() for m in materials])

        yield {
            **data,
            'materials': materials,
            'link': res.url
        }
