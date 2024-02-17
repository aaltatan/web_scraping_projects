from typing import Iterator
import scrapy
from scrapy.http import Request, Response
import logging


logging.basicConfig(
    filename="logger.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%D",
    encoding="utf-8",
)


def cfDecodeEmail(encodedString):
    r = int(encodedString[:2], 16)
    email = "".join(
        [
            chr(int(encodedString[i : i + 2], 16) ^ r)
            for i in range(2, len(encodedString), 2)
        ]
    )
    return email


class ContractorsSpider(scrapy.Spider):
    name = "contractors"
    allowed_domains = ["muqawil.org"]

    # ? scrapy crawl contractors -a end=736

    def start_requests(self) -> Iterator[Request]:
        end: int = int(self.end) + 1
        for page in range(1, end):
            request = Request(
                url=f"https://muqawil.org/ar/contractors?page={page}",
                callback=self.parse_page,
            )
            request.meta["dont_cache"] = True
            yield request

    def parse_page(self, res: Response):
        response: scrapy.Selector = res
        links = response.css("h4.card-title > a::attr(href)").getall()
        for link in links:
            yield res.follow(url=link)

    def parse(self, res: Response):
        response: scrapy.Selector = res

        title = response.css("h3.card-title::text").get().strip()

        badges = [
            badge.replace("\n", "").strip()
            for badge in response.css(".badges .badge::text").getall()
            if badge != "\n"
        ]

        badges = ", ".join(badges)

        information = {}

        selector = ".badges ~ .info-box-wrapper .row .info-box .info-details"
        information_divs = response.css(selector)
        for div in information_divs:
            key = div.css(".info-name::text").get()
            key = key.strip() if key else key

            value = div.css(".info-value::text").get()
            if div.css(".info-value a span"):
                enc_email = div.css(".info-value a span::attr(data-cfemail)").get()
                value = cfDecodeEmail(enc_email)

            information[key] = value

        yield {"title": title, "badges": badges, **information}
