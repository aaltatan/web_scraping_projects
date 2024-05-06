from scrapy.http import Request, Response, FormRequest
from urllib.parse import urlencode, parse_qs
from fake_useragent import FakeUserAgent
from typing import Iterator, Iterable
import logging
import scrapy


logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


def cf_decode_email(encodedString):
    r = int(encodedString[:2], 16)
    email = "".join(
        [
            chr(int(encodedString[i : i + 2], 16) ^ r)
            for i in range(2, len(encodedString), 2)
        ]
    )
    return email


class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.yello.ae"]

    def start_requests(self) -> Iterable[Request]:
        request = Request("https://www.yello.ae/browse-business-cities")
        request.meta["dont_cache"] = True
        return [request]
    
    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css('.cat_list li a::attr(href)').getall()
        for link in links:
            request = res.follow(res.urljoin(link), callback=self.parse_city)
            request.meta['dont_cache'] = True
            yield request

    def parse_city(self, res: Response):
        response: scrapy.Selector = res
        links = response.css(".company h4 a::attr(href)").getall()
        for link in links:
            yield res.follow(res.urljoin(link), callback=self.parse_company)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield res.follow(res.urljoin(next_page), callback=self.parse_city)

    def parse_company(self, res: Response):
        response: scrapy.Selector = res
        name = response.css("section:has(.tp.scroller) h1::text").get()
        location = "".join(response.css('.location *::text').getall()[:-1])
        phone = response.css('.text.phone::text').get()
        mobile = (
             response
             .xpath('//div[text()="Mobile phone"]/../div[@class="text"]/text()')
             .extract_first()
        )
        fax = (
             response
             .xpath('//div[text()="Fax"]/../div[@class="text"]/text()')
             .extract_first()
        )
        manager = (
            response
            .xpath('//span[text()="Company manager"]/../text()')
            .extract_first('')
            .strip()
        )
        website = (
             response
             .xpath('//div[text()="Website address"]/../div[@class="text weblinks"]/a/@href')
             .extract_first()
        )
        google_maps = response.css('#map_dir_button::attr(href)').get()
        products = (
            ", "
            .join(
                response
                .css('.cmp_list.scroller div[class="product"] .product_name *::text')
                .getall()
            )
        )
        employees = (
            ", "
            .join(
                response
                .css('.cmp_list.scroller .product.employee *::text')
                .getall()
            )
        )
        description = response.css('.text.desc::text').get()
        city =  response.css('.tp.scroller li a span::text').getall()[-2]
        category =  response.css('.tp.scroller li a span::text').getall()[-1]
        tags = ", ".join(response.css('.tags a::text').getall())

        yield {
            'name': name,
            'city': city,
            'category': category,
            'manager': manager,
            'phone': phone,
            'mobile': mobile,
            'fax': fax,
            'website': website,
            'location': location,
            'products': products,
            'employees': employees,
            'google_maps': google_maps,
            'description': description,
            'tags': tags,
            'url': res.url,
        }
