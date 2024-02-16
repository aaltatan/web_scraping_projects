import scrapy
import scrapy
from scrapy.spiders import Spider
from scrapy.http import Response
from selectolax.parser import HTMLParser
import logging

logging.basicConfig(
    filename='logger.log',
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)


class FactoriesSpider(scrapy.Spider):
    name = "factories"
    allowed_domains = ["www.egydir.com"]
    start_urls = ["https://www.egydir.com/ar/sections/factory"]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        selector = '.home__content > div > div:first-child .box1 .list-categories li'
        links = response.css(selector)
        for link in links:
            request = res.follow(
                url=link.css('a::attr(href)').get(),
                callback=self.parse_category,
                cb_kwargs={
                    'category': link.css('a::text').get().strip()
                }
            )
            request.meta['dont_cache'] = True
            yield request

    def parse_category(self, res: Response, category):
        response: scrapy.Selector = res

        selector = '.list-companies .panel .panel-body > .row > div:last-child a::attr(href)'
        links = response.css(selector).getall()

        for link in links:
            request = res.follow(
                url=link,
                callback=self.parse_item,
                cb_kwargs={
                    'category': category
                }
            )
            request.meta['dont_cache'] = True
            yield request

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            requests = res.follow(
                url=next_page,
                callback=self.parse_category,
                cb_kwargs={
                    'category': category
                }
            )
            request.meta['dont_cache'] = True
            yield request

    def parse_item(self, res: Response, category):
        parser = HTMLParser(res.text)

        # title
        title = parser.css_first('h2.company_name').text(strip=True)

        # description
        selector = '.general_data > div:has(h3 > i.fa-cog) p'
        description = ''
        if parser.css_first(selector):
            description = parser.css_first(selector).text(strip=True)

        # company owners
        employers = ''
        if parser.css('.general_data > div:has(h3 > i.fa-user)'):
            selector = '.general_data > div:has(h3 > i.fa-user) .employee > .position'
            positions = parser.css(selector)
            selector = '.general_data > div:has(h3 > i.fa-user) .employee > .employee_name'
            names = parser.css(selector)
            employers = [{k.text(strip=True): v.text(strip=True)}
                         for k, v in zip(positions, names)]

        # phones
        selector = '.general_data > div:has(h3 > i.fa-phone) p a'
        phones = ''
        if parser.css(selector):
            phones = [phone.attributes.get('href')
                      for phone in parser.css(selector)]

        # Website & emails
        contact_details = {}
        selector = '.general_data > div:has(h3 > i.fa-globe) .company_contact'
        contact_divs = parser.css(selector)
        if contact_divs:
            for div in contact_divs:
                key = div.css_first('h4').text(strip=True)
                values_div = div.css('div > a')
                values = [value.attributes.get('href')
                          for value in values_div]
                contact_details[key] = values

        # socials
        socials = ''
        selector = '.general_data > div:has(ul.socials) .social a'
        if parser.css(selector):
            socials = [social.attributes.get('href')
                       for social in parser.css(selector)]

        # branches
        branches = {}
        selector = '.company_details > div:last-child > h3'
        cities = [city.text(strip=True) for city in parser.css(selector)]

        branches_divs = parser.css('.company_details > div:last-child > div')
        for idx, div in enumerate(branches_divs):
            selector = 'p[style="padding-top: 20px"] ~ p'
            address = div.css_first(selector).text(strip=True)

            branches_contact_details = {}
            contact_details_divs = div.css('.company_contact')
            for detail in contact_details_divs:
                key = detail.css_first('h4').text(strip=True)
                values_div = div.css('p > a')
                values = [value.attributes.get('href')
                          for value in values_div]
                branches_contact_details[key] = values

            branches[cities[idx]] = {
                'address': address,
                **branches_contact_details,
            }

        yield {
            'title': title,
            'category': category,
            'description': description,
            'employers': employers,
            'phones': phones,
            'contact_details': contact_details,
            'socials': socials,
            'branches': branches,
            'link': res.url,
        }
