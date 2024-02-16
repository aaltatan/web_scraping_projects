import scrapy
from scrapy.http import Response, Request
import logging


logging.basicConfig(
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class RecsSpider(scrapy.Spider):
    name = "recs"
    allowed_domains = ["kitchen.sayidaty.net"]

    def start_requests(self) -> list[Request]:
        BASE = 'https://kitchen.sayidaty.net/%D8%A2%D8%AE%D8%B1-%D8%A7%D9%84%D9%88%D8%B5%D9%81%D8%A7%D8%AA'
        request = Request(BASE)
        request.meta['dont_cache'] = True
        return [request]

    def parse(self, response: Response):

        receipts = response.css('.section-content .column .article-item')
        main_receipt = response.css('.article-item-img > a').attrib['href']

        yield response.follow(main_receipt, callback=self.parse_receipt)

        for receipt in receipts:
            receipt_link = receipt.css('.article-item-img a').attrib['href']
            yield response.follow(receipt_link, callback=self.parse_receipt)

        next_page = response.css('a[rel="next"]').attrib['href']

        if next_page is not None:
            request = response.follow(next_page, callback=self.parse)
            request.meta['dont_cache'] = True
            yield request

    def parse_receipt(self, response: Response):

        html: scrapy.Selector = response

        texts = html.css('.intro-text p span *::text').getall()
        texts = " ".join([text.strip() for text in texts])

        contents = html.css('.ingredients-area *::text').getall()
        contents = [content.replace('\n', '').replace('-', '').strip()
                    for content in contents]
        contents = "\n".join(contents)

        image = html.css('.entry-media img')
        image = image.attrib['src'] if image else None

        preparation = html.css('.preparation-area *::text').getall()
        preparation = [p.replace('\n', '') for p in preparation if p != '\n']
        preparation = "\n".join(preparation)

        category = html.css('.breadcrumbs li a::text').getall()[-1].strip()

        selector = '.recipe-meta-field:nth-child(1) .recipe-meta-data-info span::text'
        time = html.css(selector).get()

        selector = '.recipe-meta-field:nth-child(2) .recipe-meta-data-info span::text'
        count = html.css(selector).get()

        yield {
            'text': texts,
            'time': time,
            'image': image,
            'count': count,
            'contents': contents,
            'preparation': preparation,
            'category': category,
            'link': response.url
        }
