import sys
from typing import Optional, Dict
from uuid import uuid4, UUID
from psycopg2.errors import UniqueViolation

sys.path.append('.')
from src.common.logger import CrwlLogger
from src.common.models.template import TemplateInDB


class TemplateManager():
    
    def __init__(self,
                 logger: CrwlLogger,
                 psql_connection) -> None:
        
        self.psql_connection = psql_connection  
        self._logger = logger  
    
    def save(self, template) -> Optional[Dict[str, UUID]]:
        with self.psql_connection.cursor() as cursor:
            sql = """
                INSERT INTO templates (template) VALUES (%(template)s) RETURNING id
            """
            try: 
                cursor.execute(sql, {'template': template.model_dump_json()})
                self.psql_connection.commit()
                template_uuid = cursor.fetchone()[0]
                return template_uuid
            except UniqueViolation:
                return None
            
    def delete(self, template_id: str) -> str:
        with self.psql_connection.cursor() as cursor:
            sql = """
                DELETE FROM schemas WHERE template=%(template)s;
                DELETE FROM templates WHERE id=%(template)s RETURNING id
            """
            try:
                cursor.execute(sql, {'template': template_id})
                self.psql_connection.commit()
                deleted_template_uuid = cursor.fetchone()[0]
                return deleted_template_uuid
            except BaseException as e:
                return None
    
    def get(self, template_id: str):
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT template FROM templates WHERE id = %(template_id)s
            """
            try: 
                cursor.execute(sql, {'template_id': template_id})
                template = cursor.fetchone()[0]
                return template
            except BaseException as e:
                return None
            
    def get_all(self):
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT id FROM templates
            """
            try: 
                cursor.execute(sql)
                templates_all = cursor.fetchall()
                return templates_all
            except BaseException as e:
                return None
            
    def get_schemas(self, template_id: str):
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT id FROM schemas WHERE template_uuid=%(template_id)s
            """
            try: 
                cursor.execute(sql, {'template_id': template_id})
                schema_ids = cursor.fetchall()
                return schema_ids
            except BaseException as e:
                return None
    
    def parse(self, template) -> None:
        """
        Метод для парсинга шаблона. Извлекает имена полей и их параметры для БД
        и возвращает их в виде списка словарей

        Returns:
            List[Dict[str, TemplateFieldCostraints]]: _description_
        """
        block_names = template.keys()
        res = []
        for b_name in block_names:
            block = template.get(b_name)
            field_names = block.keys()
            for f_name in field_names:
                f_constraints = block.get(f_name).get('constraints')
                field_in_res = {f_name: f_constraints}
                res.append(field_in_res)
        return res
    
    