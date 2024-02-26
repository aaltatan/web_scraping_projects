# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request

class AlalameyastorePipeline:
    def process_item(self, item, spider):
        return item


class ProductImagePipeline(ImagesPipeline):
    def file_path(self, request: Request, response=None, info=None, *, item=None):
        url: str = request.url
        print(request.meta.get('title'))
        print("#" * 100)
        filename: str = url.split("/")[-1]
        return filename
    
    def get_media_requests(self, item, info):
        url = item['image_urls']
        title = item['title']
        yield Request(url=url, meta={'title': title})