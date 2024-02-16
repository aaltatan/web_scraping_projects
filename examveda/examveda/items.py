# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ExamvedaItem(scrapy.Item):
    # define the fields for your item here like:
    ...


class QuestionItem(scrapy.Item):
    # define the fields for your item here like:
    section = scrapy.Field()
    category = scrapy.Field()
    question = scrapy.Field()
    right_answer = scrapy.Field()
    link = scrapy.Field()
    A = scrapy.Field()
    B = scrapy.Field()
    C = scrapy.Field()
    D = scrapy.Field()
    E = scrapy.Field()
