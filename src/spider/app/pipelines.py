import os
from typing import List
import pymongo
from pymongo import UpdateOne
import sys

sys.path.append('.')

from src.spider.app.processors.models import SpiderStats, SpiderError


class SpiderMainPipeline:
    def __init__(self, mongo_uri, mongo_db, spider_crawler):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.spider_crawler = spider_crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=os.environ.get('MONGO_URI', 'mongodb://crwl:Crawly97@localhost:27017'),
            mongo_db=os.environ.get('MONGO_DB', "crawly"),
            spider_crawler=crawler
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.item_collection = spider.template_uuid
        self.stat_collection = f"stat_{spider.template_uuid}"

    def close_spider(self, spider):
        if len(spider.error_list) == 0:
            self.bulk_upsert(spider)
        else:
            pass
            # Implement return error values or signaling if errors exist
        self.spider_crawler.stats.set_value("error_count", len(spider.error_list))
        self.spider_crawler.stats.set_value("errors", spider.error_list)
        self.spider_crawler.stats.set_value("spider_schema", spider.schema_uuid)
        self.spider_crawler.stats.set_value("spider_task", spider.task.task_uuid)
        self.dump_spider_stats()
        self.client.close()
        
    def bulk_upsert(self, spider):
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
        res = self.db[self.item_collection].bulk_write(mongo_operations, ordered=False)

    def dump_spider_stats(self):
        stat_obj = SpiderStats.model_validate(self.spider_crawler.stats.get_stats())
        self.db[self.stat_collection].insert_one(stat_obj.model_dump())

    def process_item(self, item, spider):
        return item