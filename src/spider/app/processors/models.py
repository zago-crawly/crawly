from dataclasses import dataclass, Field
from lxml.html import HtmlElement
from typing import List, Optional
from functools import reduce

@dataclass
class PipelineError():
    error: str

@dataclass
class SchemaBlockField():
    html_doc: HtmlElement
    field_name: str
    field_processors: dict
    output_field: dict
    index: List
    
@dataclass
class ItemTreeNodeData():
    schema_block_data: dict
    schema_block_index: any
