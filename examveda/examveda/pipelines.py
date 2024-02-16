# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ExamvedaPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        category: str = adapter.get('category')
        section: str = category.split('-')[0]
        category: str = category.split('-')[-1]

        adapter['section'] = section.lower()
        adapter['category'] = category.lower()

        return item
