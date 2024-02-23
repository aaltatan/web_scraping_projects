from scrapy.http import Request, Response
from fake_useragent import FakeUserAgent
from urllib.parse import urlencode
import logging
import scrapy
import json


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)

class CompaniesSpider(scrapy.Spider):
    name = "companies"
    allowed_domains = ["www.wcaworld.com",
                       "www.elitegln.com",
                       "www.lognetglobal.com",
                       "www.wcaecommerce.com",
                       "www.wcaworldpartnerpay.com",
                       "www.wcaworldquotationsystem.com",
                       "www.wcaperishables.com",
                       "www.wcavendors.com",
                       "www.wcaprojects.com",
                       "www.wcaworldacademy.com",
                    #    "www.iata.org",
                    #    "ifc8.network",
                       "www.globalaffinityalliance.com"]
    ua = FakeUserAgent()
    custom_headers = {
        'Referer': 'https://www.wcaworld.com/directory',
    }

    def start_requests(self) -> list[Request]:
        BASE = "https://www.wcaworld.com/Api/countries"
        request = Request(url=BASE, headers=self.custom_headers)
        request.meta['dont_cache'] = True
        return [request]

    def parse(self, res: Response):
        response: list[dict] = json.loads(res.text)
        countries: list[str] = [country.get('Code') for country in response]
        for country in countries:
            for idx in range(1,3):
                headers = {
                    'User-Agent': self.ua.random,
                    'Referer': 'https://www.wcaworld.com/directory'
                }
                BASE = f'https://www.wcaworld.com/Directory/NextV1?siteID=24&pageIndex={idx}&pageSize=100&searchby=CountryCode&country={country}&orderby=CountryCity&networkIds=1&networkIds=2&networkIds=3&networkIds=4&networkIds=61&networkIds=98&networkIds=108&networkIds=118&networkIds=5&networkIds=22&networkIds=13&networkIds=18&networkIds=15&networkIds=16&networkIds=38&networkIds=103&layout=v1&submitted=search&lastCid=0'
                request = res.follow(url=BASE, 
                                     headers=headers,
                                     callback=self.parse_page)
                request.meta['dont_cache'] = True
                yield request

    def parse_page(self, res: Response):
        response: scrapy.Selector = res

        links = response.css('.directoyname > a::attr(href)').getall()
        for link in links:
            url = link if link.startswith('https') else res.urljoin(link)
            yield {
                'url': url
            }
            # headers = {
            #     'User-Agent': self.ua.random
            # }
            # request = res.follow(url,
            #                     headers=headers, 
            #                     callback=self.parse_company)
            #                     #  callback=self.parse_company)
            # request.meta['dont_cache'] = True
            # yield request

    def parse_company(self, res: Response):
        response: scrapy.Selector = res

        name = response.css('.company_name h1::text').get('')
        branch_name = response.css('.company_name .branchname::text').get('')

        branches_container = (
            response
            .css('.office_country_wrapper .branchoffice_row')
        )
        branches: dict = {}
        for branch in branches_container:
            key = branch.css('.office_country.countryname::text').get('').strip()
            values = {l.css('a::text').get('key').strip(): 
                      l.css('a::attr(href)').get('value').strip()
                      for l in branch.css('.office_entry')}
            branches[key] = values

        date = response.css('.announce-display::text').getall()
        date = " ".join(date).strip()

        profile = response.css('.profile_table tr td::text').get('').strip()

        address = (
             response
             .xpath('//*[@class="profile_headline" and text()="Address:"]/../span/text()')
             .extract()
        )

        country = ''
        if address:
            country = address[-1]

        address = "\n".join(address)

        information: dict = {}

        for row in response.css('.profile_row'):
            key = (
                row
                .css('.profile_label::text')
                .get('')
                .strip()
                .replace(':', '')
                .lower()
            )
            value = (
                row
                .css('.profile_val *::text')
                .getall()
            )
            value = "".join(value).strip()
            information[key] = value

        yield {
            'name': name,
            'branch_name': branch_name,
            'branches': branches,
            'date': date,
            'profile': profile,
            'country': country,
            'address': address,
            'information': information,
            'url': res.url,
        }
