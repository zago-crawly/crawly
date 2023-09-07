import sys
# import re
from typing import List
from fastcore.transform import Transform
from functools import wraps

sys.path.append(".")
from src.spider.app.processors.models import SchemaBlockField, PipelineError

class StringProcessor(Transform):
    
    def type_coercion_middleware(func):
        """Функция является оберткой для строкового процессора, которая приводит
        запарсенные данные в форматах str или List[str] или List[List[str]] к формату List[str]
        и после работы процессора приводит их к исходному формату.

        Args:
            func (): Функция encodes 
        """
        @wraps(func)
        def inner(self, x: SchemaBlockField): 
            postprocessors = x.field_processors.get('postprocessors')
            field_data = x.output_field[x.field_name]    
               
            if not postprocessors:
                return x
            
            if isinstance(field_data, str):
                x.output_field[x.field_name] = [field_data]
                res = func(self, x)
                res.output_field[res.field_name] = res.output_field[res.field_name][0]
                return res
            if isinstance(field_data, list) and all([isinstance(el, str) for el in field_data]):
                res = func(self, x)
                return res
            if isinstance(field_data, list) and all([isinstance(sub_el, str) for el in field_data for sub_el in el]):
                x.output_field[x.field_name] = [sub_el for el in field_data for sub_el in el]
                res = func(self, x)
                res.output_field[res.field_name] = [[el for el in res.output_field[res.field_name]]]
                return res
            
            return x
        return inner
    
    @type_coercion_middleware
    def encodes(self, x: SchemaBlockField) -> SchemaBlockField | PipelineError:
        postprocessors = x.field_processors.get('postprocessors')
        field_data = x.output_field[x.field_name]

        prefix = postprocessors.get('prefix', "")
        suffix = postprocessors.get('suffix', "")
        strip = postprocessors.get('strip', False)
                    
        processed_data_item = []
            
        for item in field_data:
            if prefix:
                item = prefix + item
            if suffix:
                item = item + suffix
            if strip:
                item = item.strip()
            processed_data_item.append(item)    
        x.output_field[x.field_name] = processed_data_item
        
        return x
    
    def encodes(self, x: PipelineError):
        """Метод пропускающий обработку при возникновении ошибки в предыдущем обработчике

        Args:
            x (PipelineError): _description_
        """
        return x
