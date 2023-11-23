from dataclasses import dataclass
from pydantic import BaseModel, Field
from lxml.html import HtmlElement
from datetime import datetime
from typing import List, Optional
from functools import reduce

@dataclass
class SpiderError():
    error: str
    field_name: str = None

@dataclass
class SchemaBlockField():
    html_doc: HtmlElement
    field_name: str
    field_processors: dict
    index: List
    output_field: None | dict = None
    
@dataclass
class ItemTreeNodeData():
    schema_block_data: dict
    schema_block_index: any



class SpiderStats(BaseModel):
    start_time: datetime = Field(alias='start_time')
    startup_mem_usage: int = Field(alias='memusage/startup')
    max_mem_usage: int = Field(alias='memusage/max')
    spider_schema: str = Field(alias='spider_schema')
    spider_task: str = Field(alias='spider_task')
    log_warning: int = Field(default=0, alias='log_count/WARNING')
    log_error: int = Field(default=0, alias='log_count/ERROR')
    log_info: int = Field(default=0, alias='log_count/INFO')
    request_count: int = Field(default=0, alias='downloader/request_count')
    error_count: int = Field(default=0, alias='error_count')
    errors: List[SpiderError] = Field(default=[], alias='errors')
    response_received_count: int = Field(default=0, alias='response_received_count')
    response_status_count_200: int = Field(default=0, alias='downloader/response_status_count/200')
    response_status_count_404: int = Field(default=0, alias='downloader/response_status_count/404')
    response_status_count_500: int = Field(default=0, alias='downloader/response_status_count/500')
    response_bytes: int = Field(default=0, alias='httpcompression/response_bytes')
    