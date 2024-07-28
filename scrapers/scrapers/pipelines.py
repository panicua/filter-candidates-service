# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pandas as pd


class JsonWriterPipeline:

    def __init__(self):
        self.items = None

    def open_spider(self, spider):
        self.items = []

    def close_spider(self, spider):
        df = pd.DataFrame(self.items)
        df.to_json(
            "urls.json",
            orient="records",
            lines=False,
            force_ascii=False,
            indent=4,
        )

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item
