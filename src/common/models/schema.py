import sys
from typing import Any, Dict, List, Optional
from pydantic import (BaseModel,
                      Field,
                      model_validator,
                      ValidationError)

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
        inner_template = self.schema_field
        for index, block_name in enumerate(list(inner_template.keys())[:-1]):
            block = inner_template.get(block_name)
            if block:
                # block['request'] = TemplateRequest.model_validate(self._request_fields[index])
                block['pagination'] = TemplatePaginationOptional.model_validate(self._pagination_fields[index])
        return self

class SchemaCreate(SchemaBaseClass):
    template_uuid: str

class SchemaInDB(SchemaBaseClass):
    pass

class SchemaRead(SchemaBaseClass):
    template_uuid: str = Field(title="UUID шаблона схемы для парсинга")
    pass

class SchemaForTask(SchemaBaseClass):
    pass
