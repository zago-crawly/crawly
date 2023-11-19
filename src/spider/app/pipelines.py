import os
from typing import List
import pymongo
from pymongo import UpdateOne


class SpiderMainPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=os.environ.get('MONGO_URI', 'mongodb://crwl:Crawly97@localhost:27017'),
            mongo_db=os.environ.get('MONGO_DB', "crawly"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.item_collection = spider.template_uuid

    def close_spider(self, spider):
        items = spider.item_tree.get_items()
        indexes = spider.item_tree.get_indexes()
        schema_uuid = spider.schema_uuid
        mongo_operations = []
        for index, item in zip(indexes, items):
            item['__processed'] = False
            item['__hash'] = index
            item['__schema_uuid'] = schema_uuid
            mongo_operations.append(
                UpdateOne({"__hash": index},{ "$set": item },upsert=True)
                )
        self.bulk_upsert(mongo_operations)
        self.client.close()
        
    def bulk_upsert(self, operations: List):
        res = self.db[self.item_collection].bulk_write(operations, ordered=False)

    def process_item(self, item, spider):
        return item