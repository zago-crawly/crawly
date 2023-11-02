import os
import pymongo
import logging


class SpiderMainPipeline:
        
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=os.environ.get('MONGO_URI'),
            mongo_db=os.environ.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        try: 
            spider.last_item_hash = self.db[spider.template_uuid].find({}, {"__hash":1}, sort=[("_id", pymongo.ASCENDING)]).limit(1)[0].get('__hash')
        except IndexError:
            pass
        self.item_collection = spider.template_uuid

    def close_spider(self, spider):
        items = spider.item_tree.get_items()
        indexes = spider.item_tree.get_indexes()
        schema_uuid = spider.schema_uuid
        for index, item in zip(indexes, items):
            if index != spider.last_item_hash:
                item['__processed'] = False
                item['__hash'] = index
                item['__schema_uuid'] = schema_uuid
                self.insert_item(item)
            else:
                break
        self.client.close()
        
    def insert_item(self, item):
        self.db[self.item_collection].insert_one(item)

    def process_item(self, item, spider):
        return item