import sys
from fastcore.transform import Transform
from typing import Optional, Union

sys.path.append(".")
from src.spider.app.processors.models import SchemaBlockField, SpiderError

class ConstraintsProcessor(Transform):
    
    def encodes(self, x: SchemaBlockField) -> SchemaBlockField | SpiderError:
        field_name = x.field_name
        field_processors = x.field_processors
        output_field = x.output_field
        constraints = field_processors.get('constraints', '')
        parsed_field_data = output_field[field_name]
        
        if constraints:
            data_type_constr,\
            required_constr,\
            internal_data_type_const,\
            max_length,\
            index,\
            group_array_const= constraints.get('data_type'),\
                    constraints.get('required'),\
                    constraints.get('internal_type'),\
                    constraints.get('max_length'),\
                    constraints.get('index'), \
                    constraints.get('group')
                                        
            if (parsed_field_data is None or len(parsed_field_data) == 0) and required_constr == True:
                return SpiderError("Data is empty but is required")
            
            coerced_field_data = type_coercion(parsed_field_data=parsed_field_data,
                                               data_type=data_type_constr,
                                               internal_type=internal_data_type_const,
                                               group=group_array_const)
            trimmed_field_data = trim_data(parsed_field_data=coerced_field_data,
                                           max_length=max_length)
            match trimmed_field_data:
                case SpiderError():
                    return trimmed_field_data
                case _:
                    x.output_field[field_name] = trimmed_field_data
                    if index:
                        if isinstance(trimmed_field_data, list):
                            x.index += trimmed_field_data
                        else:
                            x.index.append(trimmed_field_data)
                    return x

    def encodes(self, x: SpiderError):
        """Метод пропускающий обработку при возникновении ошибки в предыдущем обработчике

        Args:
            x (SpiderError): _description_
        """
        return x
    
def trim_data(parsed_field_data, max_length: int) -> Union[str,list,int,float] | SpiderError:
    
    if isinstance(parsed_field_data, list):
        if isinstance(parsed_field_data[0], list):
            return [parsed_field_data[0][:max_length]]
        return parsed_field_data[:max_length]
    
    elif isinstance(parsed_field_data, str):
        return parsed_field_data[:max_length]
    
    elif isinstance(parsed_field_data, int):
        return int(str(parsed_field_data)[:max_length])
    
    elif isinstance(parsed_field_data, float):
        return float(str(parsed_field_data)[:max_length])
    
    else:
        return SpiderError("Param max_length oveflow. Can't trim data to specific length")

def type_coercion(parsed_field_data, data_type: str, internal_type: Optional[str], group: Optional[bool]) -> Union[str,list,int,float] | SpiderError:
    match data_type:
        case 'str':
            return coerce_to_str(parsed_field_data)
        case 'int':
            return coerce_to_int(parsed_field_data)
        case 'float':
            return coerce_to_float(parsed_field_data)
        case 'array':
            if group:
                return [coerce_to_list(parsed_field_data)]
            return coerce_to_list(parsed_field_data)

def coerce_to_str(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        try:
            return ' '.join(str(item) for item in value)
        except TypeError:
            return SpiderError(f'Coercion from list of {type(value[0]).__name__} to str failed')
    else:
        try:
            return str(value)      
        except ValueError:
            return SpiderError(f'Coercion from {type(value).__name__} to str failed')
        
def coerce_to_list(value):
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        return [value]
    else:
        return [value]

def coerce_to_int():
    pass

def coerce_to_float():
    pass