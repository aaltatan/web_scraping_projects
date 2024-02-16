import scrapy
from scrapy.http import Response
from itertools import batched
import logging


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding='utf-8',
    level=logging.INFO,
)


class QuestionsSpider(scrapy.Spider):
    name = "questions"
    allowed_domains = ["www.mbamcq.com"]
    start_urls = ["https://www.mbamcq.com/"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response\
            .css('#sidebar-wrapper > .list-group > a::attr(href)')\
            .getall()
        for link in links:
            yield res.follow(url=link, callback=self.parse_questions)

    def parse_questions(self, res: Response):
        response: scrapy.Selector = res
        category = response\
            .css('.breadcrumb .breadcrumb-item:nth-child(2) > a::text')\
            .get()

        questions = response\
            .xpath('//p[strong] | //ol[@type="A"] | //div[contains(@id, "answer")]')
        questions = batched(questions, 3)
        for q in questions:
            question, answers, right_answer = q

            question = question.xpath('text()').extract_first()
            answers = answers.xpath('.//li/text()').extract()
            right_answer = ",".join(right_answer.css('*::text').getall())
            yield {
                'category': category,
                'question': question,
                'answers': answers,
                'right_answer': right_answer,
                'url': res.url
            }

        next_page_class = response\
            .xpath('//a[text()="Next"]/@class')\
            .extract_first()

        if not next_page_class.strip().endswith('disabled'):
            next_page = response\
                .xpath('//a[text()="Next"]/@href')\
                .extract_first()
            yield res.follow(next_page, callback=self.parse_questions)
