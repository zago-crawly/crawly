from typing import Dict, Literal, Optional, Union
from typing_extensions import Annotated
from enum import Enum
from pprint import pprint
from pydantic import (BaseModel,
                      Field,
                      SerializationInfo,
                      model_validator,
                      field_validator,
                      RootModel,
                      ValidationError,
                      field_serializer,
                      ConfigDict)
from re import search as re_search


class BaseTemplateFieldType(BaseModel):
    required: Optional[bool] = False

class TemplateFieldTimeDataType(BaseTemplateFieldType):
    data_type: Literal['time']

class TemplateFieldDateDataType(BaseTemplateFieldType):
    data_type: Literal['date']

class TemplateFieldStringDataType(BaseTemplateFieldType):
    data_type: Literal['str']
    max_length: Optional[int] = Field(default=500, ge=0, le=3000)
    index: Optional[bool] = False
    
    @model_validator(mode='after')
    def check_for_max_length_for_index(cls, data):
        index = data.index
        max_length = data.max_length
        if index and max_length > 200:
            raise ValidationError('Cant use field with max_length more than 200 for index')
        return data

class TemplateFieldIntDataType(BaseTemplateFieldType):
    data_type: Literal['int']

class TemplateFieldFloatDataType(BaseTemplateFieldType):
    data_type: Literal['float']
    max_length: Optional[int] = Field(default=8, ge=0, le=24)

class ArrayDataTypesEnum(Enum):
    TemplateFieldIntDataType = 'int'
    TemplateFieldStringDataType = 'str'
    TemplateFieldFloatDataType = 'float'

class TemplateFieldListDataType(BaseTemplateFieldType):
    
    model_config = ConfigDict(use_enum_values=True)
    
    data_type: Literal['array']
    internal_type: ArrayDataTypesEnum
    max_length: Optional[int] = Field(default=30, ge=0, le=30)
    group: Optional[bool] = False

class TemplateFieldCostraints(RootModel):
    root: Annotated[Union[TemplateFieldStringDataType,
                          TemplateFieldIntDataType,
                          TemplateFieldFloatDataType,
                          TemplateFieldListDataType,
                          TemplateFieldDateDataType,
                          TemplateFieldTimeDataType],
                    Field(discriminator='data_type')]
    
class TemplateFieldCostraintsOptional(RootModel):
    root: Optional[Annotated[Union[TemplateFieldStringDataType,
                          TemplateFieldIntDataType,
                          TemplateFieldFloatDataType,
                          TemplateFieldListDataType,
                          TemplateFieldDateDataType,
                          TemplateFieldTimeDataType],
                    Field(discriminator='data_type')]] = Field(default=None)

class TemplateFieldSelectors(BaseModel):
    xpath: str = Field(title="Поле для серектора xpath")

class TemplateFieldSelectorsOptional(BaseModel):
    xpath: Optional[str] = Field(default=None)

class TemplateFieldPostprocessors(BaseModel):
    geocode: Optional[bool] = None
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    strip: Optional[bool] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    initial_date_format: Optional[str] = None
    new_date_format: Optional[str] = None

class TemplateFieldInDB(BaseModel):
    constraints: TemplateFieldCostraints

class TemplateFieldForSchema(BaseModel):
    constraints: TemplateFieldCostraints
    selectors: Optional[TemplateFieldSelectorsOptional] = TemplateFieldSelectorsOptional()
    postprocessors: Optional[TemplateFieldPostprocessors] = TemplateFieldPostprocessors()

class TemplatePagination(BaseModel):
    pagination_type: Literal['link']
    pagination_link: str

    @field_validator('pagination_link')
    def validate_pagination_link(f):
        res = re_search(r"<<.*>>", f)
        if res:
            return f
        else: raise ValueError('No <<?>> placeholder for page number')

class TemplatePaginationOptional(BaseModel):
    pagination_type: Optional[Literal['link']] = None
    pagination_link: Optional[str] = None
    
class TemplateInDB(BaseModel):
    template: Dict[str, Dict[str, TemplateFieldInDB]]
    
    @model_validator(mode='before')
    def remove_pag_field(cls, data):
        inner_data = data.get('template')
        for block_name in inner_data.keys():
            block = inner_data.get(block_name)
            if block:
                block.pop('pagination', None)
        return data

class TemplateCreate(TemplateInDB):
    pass

class TemplateRead(RootModel):
    root: Dict[str, Dict[str, TemplateFieldForSchema]]
    