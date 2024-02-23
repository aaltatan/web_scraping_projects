from typing import Iterator
import scrapy
from scrapy.http import Response, FormRequest, Request
import logging


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO,
)


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["bwallet.com.sa"]

    # ? scrapy crawl companies -O data\data.jsonl -a end=98

    def start_requests(self) -> Iterator[FormRequest]:
        BASE = "https://bwallet.com.sa/HomeAnonymous/GetAllKayans/"
        for idx in range(1, int(self.end) + 1):
            request = FormRequest(BASE,
                                  formdata={'PageNumber': str(idx)}, dont_filter=True)
            request.meta['dont_cache'] = True
            yield request

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('a.mycard::attr(href)').getall()
        for link in links:
            yield Request(res.urljoin(link), callback=self.parse_item)

    def parse_item(self, res: Response):
        response: scrapy.Selector = res
        title = (
            response
            .css('.profile-img ~ div h6::text')
            .get()
            .strip()
        )
        description = (
            response
            .css('.cayan-description .description-p > div > p::text')
            .get()
        )
        clean = lambda x: (
            x
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        contact = [clean(element) 
                   for element in response.css('.cayan-contact h4 *::text').getall()
                   if clean(element)]
        social_media = (
            response
            .css('.cayan-media a::attr(href)')
            .getall()
        )

        yield {
            'title': title,
            'description': description,
            'contact': contact,
            'social_media': social_media,
            'url': res.url,
        }
