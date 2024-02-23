from scrapy.http import Request, Response
import scrapy
import logging


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)

class FacultiesSpider(scrapy.Spider):
    name = "faculties"
    allowed_domains = ["saudibusiness.directory"]
    start_urls = [""]

    def start_requests(self) -> list[Request]:
        request: Request = Request(url='https://saudibusiness.directory/browse_categories.php')
        request.meta['dont_cache'] = True
        return [request]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links: list[str] = response.css('small a::attr(href)').getall()
        for link in links:
            request: Request = res.follow(url=link, callback=self.parse_page)
            request.meta['dont_cache'] = True
            yield request

    def parse_page(self, res: Response):
        response: scrapy.Selector = res

        links: list[str] = response.css('.panel h4 a::attr(href)').getall()

        for link in links:
            yield res.follow(url=link, callback=self.parse_faculty)

        pages: list[scrapy.Selector] = response.css('.pagination li')
        next_page = pages[-2]
        if next_page.xpath('./@class').extract_first() != 'disabled':
            next_link = next_page.css('a::attr(href)').get()
            request: Request = res.follow(url=next_link, callback=self.parse_page)
            request.meta['dont_cache'] = True
            yield request

    def parse_faculty(self, res: Response):
        response: scrapy.Selector = res
        
        name: str = (
            response
            .css('h1 span[itemprop="name"]::text')
            .get('')
            .strip()
        )
        address: str = (
             response
             .css('span[itemprop="streetAddress"]::text')
             .get('')
             .strip()
        )
        country: str = (
             response
             .css('span[itemprop="addressCountry"]::text')
             .get('')
             .strip()
        )
        google_maps_link: str = (
            response
            .css('.row-spaced .panel a.list-group-item:has(i.fa-globe)::attr(href)')
            .get('')
        )
        website: str = (
            response
            .css('.row-spaced .panel a.list-group-item:has(i.fa-external-link)::attr(href)')
            .get('')
        )
        telephone: str = (
             response
             .css('span[itemprop="telephone"]::text')
             .get('')
             .strip()
        )
        fax: str = (
             response
             .css('span[itemprop="faxNumber"]::text')
             .get('')
             .strip()
        )
        breadcrumbs: list[str] = (
            response
            .css('.breadcrumb li[itemprop="itemListElement"] a span::text')
            .getall()
        )
        _, category, subcategory = breadcrumbs
        description: str = (
            response.css('span[itemprop="description"] h2 span::text')
            .get('')
            .strip()
        )

        yield {
            'name': name,
            'category': category,
            'subcategory': subcategory,
            'description': description,
            'country': country,
            'address': address,
            'telephone': telephone,
            'fax': fax,
            'website': website,
            'google_maps_link': google_maps_link,
            'url': res.url,
        }

