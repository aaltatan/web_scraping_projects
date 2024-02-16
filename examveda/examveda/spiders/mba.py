import scrapy
from scrapy.http import Response
import logging
from itertools import zip_longest
from ..items import QuestionItem


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H-%M-%S",
    level=logging.INFO,
    encoding='utf-8'
)


class MbaSpider(scrapy.Spider):
    name = "mba"
    allowed_domains = ["www.examveda.com"]
    start_urls = ["https://www.examveda.com/mcq-question-on-commerce/",
                  'https://www.examveda.com/mcq-question-on-management/']

    def parse(self, res: Response):
        response: scrapy.Selector = res
        item = QuestionItem()

        if response.css('article.question'):

            questions_container = [question for question in response.css('article.question')
                                   if question.css('h2 .question-main')]

            for q_tag in questions_container:

                selector = '.crumbs span:nth-child(3) a span::text'
                category = response.css(selector).get()
                selector = '.crumbs span:nth-child(5) span::text'
                category += "-" + response.css(selector).get()

                question_text = q_tag.css('h2 .question-main::text').get()
                if q_tag.css('h2 .question-main > *'):
                    selector = 'h2 .question-main > *::text'
                    additional_text = q_tag.css(selector).getall()
                    question_text += "\n" + " ".join(additional_text)

                if q_tag.css('h2 .question-main code'):
                    selector = 'h2 .question-main code *::text'
                    code = q_tag.css(selector).getall()[0]
                    question_text += "\n" + code

                selector = '.question-inner > div > div > p.hidden input::attr(value)'
                right_answer = q_tag.css(selector).get()

                selector = '.question-inner > div > div > p:not(.hidden)'
                answers_tag = q_tag.css(selector)
                answers = ["\n".join(a.css('label:last-child *::text').getall())
                           for a in answers_tag]
                answers = {k: v for k, v in
                           zip_longest(list('ABCDE'), answers)}

                item['category'] = category
                item['question'] = question_text
                item['right_answer'] = right_answer
                item['link'] = res.url
                for letter in list('ABCDE'):
                    item[letter] = answers[letter]

                yield item

            # next page
            pages = response.css('.pagination a::attr(href)').getall()
            for page in pages:
                yield res.follow(page, callback=self.parse)

            # sections
            if response.css('.chapter-section'):
                selector = '.chapter-section a::attr(href)'
                sections_links = response.css(selector).getall()[1:]
                for link in sections_links:
                    yield res.follow(link, callback=self.parse)

        else:

            selector = '.page-content.page-shortcode article h3 a::attr(href)'
            links = response.css(selector).getall()
            for link in links:
                yield res.follow(link, callback=self.parse)
