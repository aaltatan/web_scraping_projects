import scrapy
from scrapy.http import Response
from fake_useragent import FakeUserAgent
import logging
from itertools import zip_longest
from typing import Iterator


logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


class DevicesSpider(scrapy.Spider):
    name = "devices"
    allowed_domains = ["www.gsmarena.com"]

    def start_requests(self) -> Iterator[scrapy.Request]:
        BASE = "https://www.gsmarena.com/makers.php3"
        request = scrapy.Request(url=BASE)
        request.meta['dont_cache'] = True
        yield request

    def parse(self, res: Response):
        ua = FakeUserAgent()
        response: scrapy.Selector = res
        links = response.css(".st-text a::attr(href)").getall()
        for link in links:
            request = res.follow(
                url=link,
                headers={"User-Agent": ua.random},
                callback=self.parse_category,
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_category(self, res: Response):
        ua = FakeUserAgent()
        response: scrapy.Selector = res

        links = response.css(".makers a::attr(href)").getall()
        for link in links:
            yield res.follow(
                url=link,
                headers={"User-Agent": ua.random},
                callback=self.parse_phone,
            )

        next_page = response.xpath(
            '//a[@title = "Next page"]/@href').extract_first()
        if next_page:
            request = res.follow(
                url=res.urljoin(next_page),
                callback=self.parse_category,
                headers={"User-Agent": ua.random},
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_phone(self, res: Response):
        response: scrapy.Selector = res

        title = response.css('h1[data-spec="modelname"]::text').get()

        tables = response.css("table")
        information: dict = {}

        key = ""
        for table in tables:
            table_data = {}
            specification_parent = table.css('th[scope="row"]::text').get()

            for tr in table.css('tr'):
                if tr.xpath('./text()') != "":
                    value = tr.css('.nfo *::text').getall()
                    value = (
                        ", "
                        .join(value)
                        .replace('\n', "")
                        .replace('\r', "")
                        .strip()
                    )
                    if tr.css('.ttl a'):
                        key = tr.css('.ttl a::text').get()
                        table_data[key] = value
                    else:
                        table_data[key] = table_data.get(key, "") \
                            + f", {value}"

            information[specification_parent] = table_data

        yield {"title": title,
               "information": information,
               "url": res.url}
