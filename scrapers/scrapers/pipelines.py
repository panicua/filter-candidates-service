# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pandas as pd


class JsonWriterPipeline:

    def open_spider(self, spider):
        self.items = []  # Initialize an empty list to store items

    def close_spider(self, spider):
        # Convert the list of items to a pandas DataFrame
        df = pd.DataFrame(self.items)
        # Write the DataFrame to a JSON file
        df.to_json(
            "urls.json",
            orient="records",
            lines=False,
            force_ascii=False,
            indent=4,
        )

    def process_item(self, item, spider):
        # Append each item to the list
        self.items.append(dict(item))
        return item


# class ScrapersPipeline:
#     def process_item(self, item, spider):
#         return item
