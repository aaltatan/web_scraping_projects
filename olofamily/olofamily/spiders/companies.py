import scrapy
from scrapy.http import Response

class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.olofamily.com"]
    start_urls = ["https://www.olofamily.com/Member/Company_1.html"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = (
            response
            .css('.memberlist-center-right-content-tit-font::attr(onclick)')
            .getall()
        )
        links = [
            link.replace("window.open('", "").replace("')", "") 
            for link in links
        ]
        for link in links:
            yield res.follow(
                        url=res.urljoin(link),
                        callback=self.parse_company
                    )

        next_page = response.xpath('//a[text()=">"]/@href').extract_first()
        if next_page:
            yield res.follow(
                        url=next_page,
                        callback=self.parse
                    )

    def parse_company(self, res: Response):
        response: scrapy.Selector = res

        info = response.css('.shop-jj-right li::text').getall()
        data = {
            i.split(':', 1)[0].strip(): i.split(':', 1)[-1].strip() 
            for i in info
        }

        yield {
            'name': response.css('title::text').get(''),
            'url': res.url,
            **data
        }
