from typing import Any
import scrapy
from loguru import logger
from scrapy.http import Request, Response
from scrapy.utils.log import configure_logging


configure_logging(install_root_handler=False)
logger.remove()
logger.add(lambda msg: logger.debug(msg, diagnose=False), level='DEBUG')


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.eyeofriyadh.com"]
    start_urls = ["https://www.eyeofriyadh.com/ar/directory/?location=all"]

    def __init__(self, name: str | None = None, **kwargs: Any):
        
        super().__init__(name, **kwargs)

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('.content_left .col-md-3.col-sm-3.col-xs-3 a::attr(href)').getall()
        links = list(set(links))
        for link in links:
            yield res.follow(
                        url=res.urljoin(link),
                        callback=self.parse_company,
                    )

        next_page = response.xpath('//a[text()="التالي »"]/@href').extract_first()
        if next_page:
            yield res.follow(
                        url=res.urljoin(next_page),
                        callback=self.parse
                    )

    def parse_company(self, res: Response):
        response: scrapy.Selector = res

        yield {'title': res.css('title::text').get('').strip()}
