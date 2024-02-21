import asyncio
import json
import sys
from typing import MutableMapping
from uuid import uuid4
import aio_pika
from fastapi import APIRouter
from pydantic import ValidationError


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.common.models.schema import SchemaInDB, SchemaRead
from src.common.psql_connection_pool import PSQLConnectionPool
from src.schema_storage.app.schema_manager import SchemaManager, SchemaManagerError
from src.schema_storage.app.schema_storage_app_svc_settings import SchemaStorageAppSettings


class SchemaStorageApp(AppSvc):

    _outgoing_commands = {
        "created": "schema.created",
        "mayUpdate": "schema.mayUpdate",
        "updating": "schema.updating",
        "updated": "schema.updated",
        "mayDelete": "schema.mayDelete",
        "deleting": "schema.deleting",
        "deleted": "schema.deleted"
    }

    def __init__(self, settings: SchemaStorageAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.psql_connection_pool = PSQLConnectionPool()
        
    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    def _set_incoming_commands(self) -> dict:
        return {
            "schema.create": self._create,
            "schema.read": self._read,
            "schema.read_all": self._read_all,
            "schema.update": self._update,
            "schema.delete": self._delete,
            "schema.get_template_by_schema": self._get_template_by_schema
        }

    async def _read(self, mes) -> dict:
        schema_id = mes.get('data')
        with self.psql_connection_pool.connect() as conn:
            schema_manager = SchemaManager(logger=self._logger, psql_connection=conn)
            res = schema_manager.get(schema_id=schema_id)
            if isinstance(res, SchemaManagerError):
                return {"error": {"code": "404", "message": f"{res.err}"}}
            processed_schema = SchemaRead.model_validate(res)
            return processed_schema.model_dump(by_alias=True)
        
    async def _read_all(self, mes) -> dict:
        with self.psql_connection_pool.connect() as conn:
            schema_manager = SchemaManager(logger=self._logger, psql_connection=conn)
            schemas_all = schema_manager.get_all()
            if isinstance(schemas_all, SchemaManagerError):
                return {"error": {"code": "404", "message": f"{schemas_all.err}"}}
            if len(schemas_all) > 0:
                schema_processed_all = []
                for schema_row in schemas_all:
                    schema_id = schema_row[0]
                    schema_name = schema_row[1]
                    schema_processed_all.append({"id": schema_id, "name": schema_name})
                return schema_processed_all
        
    async def _create(self, mes) -> dict:
        schema = mes.get('data')
        inner_schema = mes.get('data').get("schema")
        with self.psql_connection_pool.connect() as conn:
            template_uuid = schema.get('template_uuid', None)
            try:
                schema_processed = SchemaInDB.model_validate(schema)
            except ValidationError as e:
                return {"error": {"message": e}}
            schema_manager = SchemaManager(logger=self._logger, psql_connection=conn)
            template = await self._post_message(
                mes={"action": "template.read", "data": template_uuid}, reply=True
            ) # TODO think about data transfering between microservices
            if template.get('error'):
                return template
            if not schema_manager.verify(reference=template, schema=inner_schema):
                return {"error": {"message": f"Schema and template {template_uuid} has different structure"}}
            schema_uuid = schema_manager.save(schema=schema_processed, template_uuid=template_uuid)
            if not schema_uuid:
                return {"error": {"message": "Insertion error"}}
            return {"id": schema_uuid} 

    async def _delete(self, mes) -> bool:
        schema_id = mes.get('data')
        with self.psql_connection_pool.connect() as conn:
            schema_manager = SchemaManager(logger=self._logger, psql_connection=conn)
            deleted_schema_id = schema_manager.delete(schema_id=schema_id)
            if deleted_schema_id:
                return {"id": deleted_schema_id}
            else:
                return {"error": {"code": "404", "message": f"Schema with id {schema_id} not found"}}

    async def _update(self, mes) -> dict:
        schema_id = mes.get("data").get("id")
        updating_schema = mes.get("data").get("payload")
        with self.psql_connection_pool.connect() as conn:
            schema_manager = SchemaManager(logger=self._logger, psql_connection=conn)
            schema_in_db = schema_manager.get(schema_id=schema_id)
            validated_schema_in_db = SchemaInDB.model_validate(schema_in_db)
            if isinstance(schema_in_db, SchemaManagerError):
                return {"error": {"code": "404", "message": f"Schema with id {schema_id} not found"}}
            if not schema_manager.verify(reference=schema_in_db.get("schema"),
                                         schema=updating_schema.get("schema")):
                return {"error": {"code": "422", "message": f"New schema has different structure"}}
            try:
                updating_schema['schema_field'] = updating_schema.pop('schema')
                updating_schema = validated_schema_in_db.model_copy(update=updating_schema, deep=True)
            except ValidationError as e:
                return {"error": {"code": "500", "message": f"{e}"}}
            updated_schema = schema_manager.update(new_schema= updating_schema,schema_id=schema_id)
            # if isinstance(updated_schema, SchemaManagerError):
            #     return {"error": {"code": "404", "message": f"{updated_schema.err}"}}
            # else:
            return updated_schema

    async def _get_template_by_schema(self, mes) -> dict:
        schema_uuid = mes.get('data')
        with self.psql_connection_pool.connect() as conn:
            schema_manager = SchemaManager(logger=self._logger, psql_connection=conn)
            res = schema_manager.get_template_by_schema(schema_id=schema_uuid)
            if isinstance(res, SchemaManagerError):
                return {"error": res.err}
            return {"id": res} # TODO implement error handling if response from schema manager is an error

    async def on_startup(self) -> None:
        await super().on_startup()
        self.psql_connection_pool.create_pool()
        
    async def on_shutdown(self) -> None:
        await super().on_shutdown()
        self.psql_connection_pool.close_pool()
    
settings = SchemaStorageAppSettings()

app = SchemaStorageApp(settings=settings, title="`SchemaStorageApp` service")
