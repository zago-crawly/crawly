from dataclasses import dataclass
from typing import List

@dataclass
class PipelineError():
    error: str
@dataclass
class SchemaBlockField():
    field_name: str
    field_processors: dict
    output_field: dict
    index: List
