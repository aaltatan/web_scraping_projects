import scrapy
from scrapy.http import Response


class ArabicSpider(scrapy.Spider):
    name = "arabic"
    allowed_domains = ["www.easyel.net"]
    start_urls = ["https://www.easyel.net/2020/03/39-1440.html",
                  "https://www.easyel.net/2020/05/39-38.html",
                  ]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        questions = response\
            .css('#quiz_container > .quiz_container > li.single_question')
        for q in questions:
            question = q\
                .css('.question .text::text')\
                .get()
            answers = q\
                .css('.options li::text')\
                .getall()
            right_answer = q\
                .xpath('./@data-correct-answer')\
                .extract_first()
            yield {
                'question': question,
                'right_answer': right_answer,
                'answers': answers,
                'url': res.url
            }
