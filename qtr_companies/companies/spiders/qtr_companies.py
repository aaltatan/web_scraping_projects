import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response
import logging

logging.basicConfig(
    level=logging.CRITICAL,
    format='[%(asctime)s] {%(name)s} %(levelname)s:  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="saved_logs.log",
    encoding='utf-8'
)


def cf_decode_email(encodedString):
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r)
                    for i in range(2, len(encodedString), 2)])
    return email


class QtrCompaniesSpider(CrawlSpider):
    name = "qtr_companies"
    allowed_domains = ["www.qtr.company"]
    start_urls = ["https://www.qtr.company/"]

    rules = (
        Rule(LinkExtractor(allow=r"section\-\d+", deny=r'lang')),
        Rule(LinkExtractor(allow=r"section.+page", deny=r'lang')),
        Rule(
            LinkExtractor(allow=r"site\-\d+", deny=r'lang'),
            follow=True,
            callback='parse_item'
        ),
    )

    def parse_item(self, res: Response):
        response: scrapy.Selector = res

        information = {}
        paragraphs = response.css('#site_info > p')

        for p in paragraphs:
            key = p.css('span::text').get()
            key = key.strip() if key else key

            value = p.css('*:not(span)::text').getall()
            value = " ".join([v.strip() for v in value])

            if p.css('a.__cf_email__'):
                information['email'] = cf_decode_email(
                    p.css('a.__cf_email__::attr(data-cfemail)').get()
                )

            if p.css('a.btn'):
                information['website'] = p.css('a.btn::attr(href)').get()

            if key and value:
                information[key] = value

        values = response.css('#site_info > a::attr(href)').getall()
        keys = response.css('#site_info > a *::text').getall()
        contact_details = {k.strip(): v.strip()
                           for k, v in zip(keys, values)}

        yield {
            **information,
            **contact_details,
            'link': res.url
        }
