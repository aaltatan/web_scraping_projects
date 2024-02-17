from typing import Iterator
import scrapy
from scrapy.http import FormRequest, Response
from urllib.parse import parse_qs
import logging


logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    level=logging.INFO,
    encoding="utf-8",
)


def params(idx: str, branch: str, city: str) -> str:
    return f"branch={branch}&sub-branch=p50&city={city}&stnumber={idx}"


class ResultsSpider(scrapy.Spider):
    name = "results"
    allowed_domains = ["2023.moed.gov.sy"]

    def start_requests(self) -> Iterator[FormRequest]:

        # ? scrapy crawl results -a start=0 -a end=30000

        BASE = "https://2023.moed.gov.sy/sec-ch2/12th/resultpage.php"

        for idx in range(int(self.start), int(self.end)):
            for city in range(1, 15):
                for branch in range(1, 3):
                    formdata = {
                        k: v[0] for k, v in parse_qs(params(idx, branch, city)).items()
                    }
                    request = FormRequest(
                        url=BASE,
                        formdata=formdata,
                        dont_filter=True,
                    )
                    logging.info(formdata)
                    yield request

    def parse(self, res: Response):
        response: scrapy.Selector = res

        if response.css(".student-info-con"):
            container = response.css(".student-info-con .info-row")
            keys = [
                " ".join(key.css("div:first-child *::text").getall()).strip()
                for key in container
            ]
            values = [
                " ".join(value.css("div:last-child *::text").getall()).strip()
                for value in container
            ]

            info = {k: v for k, v in zip(keys, values)}

            subjects = response.css(".subject-con")
            for subject in subjects:
                yield {
                    **info,
                    "title": subject.css(".subject-title::text").get().strip(),
                    "mark": (
                        subject.css(".subject-mark span:last-child::text").get().strip()
                    ),
                    "min": (
                        subject.css(".min-max .min span:last-child::text").get().strip()
                    ),
                    "max": (
                        subject.css(".min-max .max span:last-child::text").get().strip()
                    ),
                }
