import json
import logging
import sys
from itertools import repeat, zip_longest
from typing import List, Optional

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.spiders.crawl import CrawlSpider
from scrapy.crawler import CrawlerProcess
import validators
from urllib.parse import urljoin
from fastcore.transform import Pipeline
from lxml.html import fromstring

sys.path.append(".")
from src.common.models.task import TaskForSpider
from src.spider.app.item_tree import ItemNodeChildrenOverflow, ItemTree
from src.spider.app.processors.constraints_processor import \
    ConstraintsProcessor
from src.spider.app.processors.models import SpiderError, SchemaBlockField
from src.spider.app.processors.selector_processor import SelectorProcessor


class Spider(CrawlSpider):
    name = "Spider"

    custom_settings = {
        'LOG_LEVEL': "DEBUG",
        'ITEM_PIPELINES': {
            'src.spider.app.pipelines.SpiderMainPipeline': 500,
        },
    }

    def __init__(self, task, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        self.task = TaskForSpider.model_validate(task)
        self.spider_settings = self.task.settings
        self._task_id: str = self.task.task_uuid
        self.schema: dict = self.task.schema_for_spider
        self.template_uuid: str = self.task.template_uuid
        self.schema_uuid: str = self.task.schema_uuid
        self.name: str = self._task_id
        self.domain: str = self.task.resource_url
        self.allowed_domains: str = self.domain
        self.base_url = self.domain if self.domain[-1] == "/" else self.domain+"/"
        self.item_tree: ItemTree = ItemTree(maxchildren=self.spider_settings.max_items)
        self.last_item_hash: Optional[str] = None
        self.error_list: List[SpiderError] = []
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Spider, cls).from_crawler(crawler, *args, **kwargs)
        return spider
    
    @property
    def schema_block_keys(self):
        return [key for key in self.schema.keys()]

    def start_requests(self):
        logging.info("Starting spider")
        yield scrapy.FormRequest(url=self.domain, callback=self.parse, cb_kwargs={'level': 0})

    def parse_schema_block(self, response, schema_block: dict, parent_node=None):
        pagination = schema_block.pop('pagination', "")
        parsed_schema_blocks = []
        for block_field_name, block_field_processors in schema_block.items():
            new_schema_block_field = SchemaBlockField(html_doc=fromstring(response.text),
                                       field_name=block_field_name,
                                       field_processors=block_field_processors,
                                       output_field={block_field_name: ""},
                                       index=[])
            processed_block = self.parse_schema_field(schema_block_field=new_schema_block_field)
            parsed_schema_blocks.append(processed_block)
        return parsed_schema_blocks

    @staticmethod
    def equalize_lists(lists):
        max_length = max([len(i) for i in lists if isinstance(i, list)], default=1)
        for i in range(len(lists)):
            value = lists[i]
            if isinstance(value, list | tuple):
                delta = max_length - len(value)
                value += list(repeat(value[-1], delta))
            else:
                lists[i] = [value for _ in range(max_length)]
        return lists
            
    def group_block_keys_indexes_values(self, schema_block: List[SchemaBlockField]) -> List[tuple]:
        block_values, block_keys, block_indexes = [], [], []
        for field in schema_block:
            block_values.append(*field.output_field.values())
            block_keys.append(*field.output_field.keys())
            if field.index: 
                block_indexes.append(field.index)
        block_indexes = list(zip_longest(*self.equalize_lists(block_indexes)))
        block_values = self.equalize_lists(block_values)
        groups = []
        for i, element in enumerate(zip_longest(*block_values, fillvalue=None)):
            item = {block_keys[i]: el for i, el in enumerate(element)}
            item_with_index = (block_indexes[i], item) if block_indexes else (None, item)
            groups.append(item_with_index)
        return groups

    def make_item_tree_nodes(self, index, block, parent_node): 
        try:
            new_node_item = self.item_tree.add(new_key=1,
                                               data=block,
                                               parent_node=parent_node,
                                               index=index)
            return new_node_item
        except ItemNodeChildrenOverflow:
            raise   
            
    def parse_schema_field(self, schema_block_field: SchemaBlockField) -> SchemaBlockField:
        field_pipeline = Pipeline([SelectorProcessor,
                                   ConstraintsProcessor])
        processed_field: SchemaBlockField | SpiderError = field_pipeline(schema_block_field)
        if isinstance(processed_field, SchemaBlockField):
            return processed_field
        elif isinstance(processed_field, SpiderError):
            processed_field.field_name = schema_block_field.field_name
            schema_block_field.output_field[schema_block_field.field_name] = processed_field.error
            self.error_list.append(processed_field)
            return schema_block_field
    
    def request_url_check(self, requests: List[str]):
        checked_request_urls = []
        for request_url in requests:
            url_is_valid = validators.url(request_url)
            if url_is_valid:
                checked_request_urls.append(request_url)
            else:
                joined_url = urljoin(self.base_url, request_url)
                joined_url_is_valid = validators.url(joined_url)
                if joined_url_is_valid:
                    checked_request_urls.append(joined_url)
                else:
                    continue
        return checked_request_urls
    
    def parse(self, response, **kwargs):
        level = kwargs.get('level')
        schema_block = self.schema[self.schema_block_keys[level]]
        parent_node = kwargs.get('parent_node')
        parsed_block: List[SchemaBlockField] = self.parse_schema_block(response,
                                                                  schema_block=schema_block,
                                                                  parent_node=parent_node)
        grouped_blocks = self.group_block_keys_indexes_values(schema_block=parsed_block)
        for index, block in grouped_blocks:
            try:
                new_item_tree_node = self.make_item_tree_nodes(index=index,
                                                                block=block,
                                                                parent_node=parent_node)
            except ItemNodeChildrenOverflow:
                break
            
            next_requests = block.pop('request', [])
            next_requests = [next_requests] if isinstance(next_requests, str) else next_requests # !!!! May be removed
            checked_requests = self.request_url_check(next_requests)
            for request_url in checked_requests:
                yield scrapy.FormRequest(url=request_url,
                                        dont_filter=True,
                                        callback=self.parse,
                                        cb_kwargs={'level': level + 1, 'parent_node': new_item_tree_node})