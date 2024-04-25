from scrapy.http import Response, FormRequest
from urllib.parse import parse_qs
import logging
import scrapy
from pathlib import Path


logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)

def cf_decode_email(encodedString):
        r = int(encodedString[:2],16)
        email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
        return email


class PdfsSpider(scrapy.Spider):
    name = "pdfs"
    allowed_domains = ["www.zvg-portal.de"]
    start_urls = ["https://www.zvg-portal.de/index.php?button=Termine%20suchen"]

    def parse(self, res: Response):
        BASE = 'https://www.zvg-portal.de/index.php?button=Suchen&all=1'
        response: scrapy.Selector = res
        regions = (
             response
             .css('select[name="land_abk"] option::attr(value)')
             .getall()[1:]
        )
        for r in regions:
             formdata = {'ger_name': '--+Alle+Amtsgerichte+--',
                         'order_by': '2',
                         'land_abk': r}
             yield FormRequest(
                  url=BASE,
                  method='POST',
                  formdata=formdata,
                  callback=self.parse_links,
                  cb_kwargs={'ref': BASE},
             )

    def parse_links(self, res: Response, ref:str):
        response: scrapy.Selector = res
        links = response.xpath('//td/a/@href').extract()
        for link in links:
            link = res.urljoin(link)
            yield res.follow(
                 url=link,
                 callback=self.parse_pdf,
                 headers={'Referer': ref}
            )

    def parse_pdf(self, res:Response):
         filename: str = res.url
         filename: str = filename.split("?")[-1]
         filename = parse_qs(filename)['file_id'][0] + '.pdf'
         directory = Path.cwd() / 'pdf_folder'
         with open(directory / filename, 'wb') as file:
              file.write(res.body)