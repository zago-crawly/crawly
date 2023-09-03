import sys
from typing import Optional, Dict
from uuid import uuid4, UUID
from psycopg2.errors import UniqueViolation

sys.path.append('.')
from src.common.models.schema import SchemaInDB
from src.common.logger import CrwlLogger


class SchemaManager():
    
    def __init__(self,
                 logger: CrwlLogger,
                 psql_connection) -> None:
        
        self.psql_connection = psql_connection  
        self._logger = logger  
    
    def save(self, schema: SchemaInDB, template_uuid: str) -> Optional[Dict[str, UUID]]:
        with self.psql_connection.cursor() as cursor:
            sql = """
                INSERT INTO schemas (schema, template) VALUES (%(schema)s, %(template_uuid)s) RETURNING id
            """
            cursor.execute(sql, {'schema': schema.model_dump_json(by_alias=True), "template_uuid": template_uuid})
            self.psql_connection.commit()
            schema_uuid = cursor.fetchone()[0]
            return schema_uuid
    
    def verify(self, template: dict, schema: dict) -> bool:
        inner_schema = schema.get('schema')
        template_block_keys = template.keys()
        schema_block_keys = inner_schema.keys()
        for t_b_key, s_b_key in zip(template_block_keys, schema_block_keys):
            if t_b_key != s_b_key:
                return False
            template_field_keys = template.get(t_b_key)
            schema_field_keys = inner_schema.get(s_b_key)
            for t_f_key, s_f_key in zip(template_field_keys, schema_field_keys):
                if t_f_key != s_f_key:
                    return False
        return True
            
    
    def get(self, schema_id):
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT schema FROM schemas WHERE id = %(schema_id)s
            """
            try:
                cursor.execute(sql, {'schema_id': schema_id})
                schema = cursor.fetchone()[0]
                self._logger.info(schema)
                return schema
            except BaseException as e:
                return {"error": str(e)}
    