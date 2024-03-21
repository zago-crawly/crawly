import sys
from typing import Any, Dict, List, Optional
from pydantic import (BaseModel,
                      Field,
                      model_validator,
                      ValidationError)
from pydantic_core import PydanticCustomError
import logging


sys.path.append(".")
from src.common.models.template import (TemplateFieldForSchema,
                                        TemplatePaginationOptional) 


class SchemaBaseClass(BaseModel):
    
    schema_field: Dict[str, Dict[str, TemplateFieldForSchema]] = Field(alias='schema', validation_alias='schema', serialization_alias='schema')
    _request_fields: List
    _pagination_fields: List    
    
    @model_validator(mode='before')
    def remove_req_pag_fields(cls, data):
        inner_data = data.get('schema')
        cls._request_fields = []
        cls._pagination_fields = []
        for block_name in list(inner_data.keys())[:-1]:
            block = inner_data.get(block_name)
            if block:
                try:
                    # request_field = TemplateRequest.model_validate(block.pop('request', {})).model_dump()
                    # cls._request_fields.append(request_field)
                    pagination_field = TemplatePaginationOptional.model_validate(block.pop('pagination', {})).model_dump()
                    cls._pagination_fields.append(pagination_field)
                except ValidationError:
                    raise
        return data
    
    @model_validator(mode='after')
    def add_validate_req_pag_fields(self):
        inner_schema = self.schema_field
        for index, block_name in enumerate(list(inner_schema.keys())[:-1]):
            block = inner_schema.get(block_name)
            if block:
                block['pagination'] = TemplatePaginationOptional.model_validate(self._pagination_fields[index])
        return self


class SchemaCreate(SchemaBaseClass):
    template_uuid: str

    @model_validator(mode='after')
    def check_index_exists(self):
        index_exists = False
        for block in self.schema_field.values():
            for field in block.values():
                field_dict = field.model_dump()
                if not field_dict.get('constraints'):
                    continue
                logging.info(field_dict.get("constraints"))
                if field_dict.get('constraints').get('index'):
                    index_exists = True
        if not index_exists:
            raise PydanticCustomError('No index field',
                                      "No index field in schema. Please add index flag on one of the field in schema")
        return self


class SchemaInDB(SchemaBaseClass):
    pass


class SchemaUpdate(BaseModel):
    schema_field: Dict[str, Dict[str, TemplateFieldForSchema]] = Field(alias='schema', validation_alias='schema', serialization_alias='schema')
    _request_fields: List
    _pagination_fields: List


class SchemaRead(SchemaBaseClass):
    template_uuid: str = Field(title="UUID шаблона схемы для парсинга")
    pass


class SchemaForTask(SchemaBaseClass):
    pass
