import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Response
import logging


logging.basicConfig(
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class QsSpider(CrawlSpider):
    name = "qs"
    allowed_domains = ["www.freetimelearning.com"]
    start_urls = [
        "https://www.freetimelearning.com/computer-science-engineering-quiz.php",
        "https://www.freetimelearning.com/civil-engineering-quiz.php",
        'https://www.freetimelearning.com/mechanical-engineering-quiz.php',
        'https://www.freetimelearning.com/electronics-and-communication-engineering.php',
        'https://www.freetimelearning.com/electrical-engineering.php'
    ]

    rules = (Rule(LinkExtractor(allow='online-quiz'), callback='parse_page'),)

    def parse_page(self, response: Response):
        links = response.css('.pagination li a::attr(href)').getall()
        for link in links:
            request = response.follow(link, self.parse_item)
            request.meta['dont_cache'] = True
            yield request

    def parse_item(self, response: Response):
        res: scrapy.Selector = response
        questions = res.css('form > .shadow-sm')
        for qc in questions:
            selector = '.quiz-question .row .question .question-right:nth-child(2)'
            question = qc.css(selector)

            code = ''
            if question.css('code'):
                code = question.css('code *::text').getall()[0]

            selector = 'a::text' if question.css('a::text').get() else '::text'
            question = question.css(selector).get()

            question = question + '\n' + code if code else question

            answers_tags = qc.css('.quiz-question-answer .row')
            answers = []
            for answer_tag in answers_tags:
                code = ''
                if answer_tag.css('.question .quiz-ans-margin code'):
                    answer = answer_tag.css(
                        '.question .quiz-ans-margin::text')
                    answer = answer.get() + '\n' if answer else ''
                    code = answer_tag.css(
                        '.question .quiz-ans-margin code *::text').getall()[0]
                    answer = answer + code
                else:
                    answer = answer_tag.css(
                        '.question .quiz-ans-margin::text').get()
                answers.append(answer)

            answers = {str(k): v for k, v in enumerate(answers, 1)}

            yield {
                'section': res.css('.breadcrumb .breadcrumb-item:nth-child(3) a::text').get(),
                'category': res.css('.example_prog_text::text').get(),
                'question': question,
                'right_answer': qc.css('.ans-text-color::text').get(),
                'link': response.url,
                **answers
            }
