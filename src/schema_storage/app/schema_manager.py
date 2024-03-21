import sys
from typing import Optional, Dict
from uuid import uuid4, UUID

sys.path.append('.')
from src.common.models.schema import SchemaInDB
from src.common.logger import CrwlLogger


class SchemaManagerError(Exception):
    def __init__(self, err: str) -> None:
        self.err = err
        super().__init__(self.err)


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

    def delete(self, schema_id: str):
        with self.psql_connection.cursor() as cursor:
            sql = """
                DELETE FROM schemas WHERE id=%(schema_id)s RETURNING id
            """
            cursor.execute(sql, {'schema_id': schema_id})
            self.psql_connection.commit()
            deleted_schema_uuid = cursor.fetchone()[0]
            return deleted_schema_uuid

    def update(self, new_schema: SchemaInDB, schema_id: str):
        with self.psql_connection.cursor() as cursor:
            sql = """
                UPDATE schemas SET schema=%(new_schema)s WHERE id=%(schema_id)s RETURNING schema
            """
            cursor.execute(sql, {'new_schema': new_schema.model_dump_json(by_alias=True),'schema_id': schema_id})
            self.psql_connection.commit()
            updated_schema = cursor.fetchone()[0]
            return updated_schema

    def verify(self, reference: dict, schema: dict) -> bool:
        reference_block_keys = reference.keys()
        schema_block_keys = schema.keys()
        for r_b_key, s_b_key in zip(reference_block_keys, schema_block_keys):
            if r_b_key != s_b_key:
                return False
            reference_field_keys = reference.get(r_b_key)
            schema_field_keys = schema.get(s_b_key)
            for r_f_key, s_f_key in zip(reference_field_keys, schema_field_keys):
                if r_f_key != s_f_key:
                    return False
        return True

    def get(self, schema_id):
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT schema, template FROM schemas WHERE id = %(schema_id)s
            """
            try:
                cursor.execute(sql, {'schema_id': schema_id})
                res = cursor.fetchone()
                if res:
                    schema, template_uuid = res
                    return {"schema": schema.get('schema'), "template_uuid": template_uuid}
                else:
                    return None
            except BaseException as e:
                return SchemaManagerError(err=str(e))
            # TODO Standardize error handling in Template manager and Schema manager (disgusting)

    def get_all(self):
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT id, name FROM schemas;
            """
            try:
                cursor.execute(sql)
                schemas_all = cursor.fetchall()
                self._logger.error(schemas_all)
                return schemas_all
            except BaseException as e:
                return SchemaManagerError(err=str(e))

    def get_template_by_schema(self, schema_id) -> dict | str:
        with self.psql_connection.cursor() as cursor:
            sql = """
                SELECT template FROM schemas WHERE id = %(schema_id)s
            """
            try:
                cursor.execute(sql, {'schema_id': schema_id})
                template_uuid = cursor.fetchone()[0]
                self._logger.info(template_uuid)
                return template_uuid
            except BaseException as e:
                return SchemaManagerError(err=str(e))
