import asyncio
import json
import sys
from typing import MutableMapping, Optional
from uuid import uuid4
import aio_pika
from fastapi import APIRouter


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.common.models.template import TemplateInDB, TemplateRead
from src.common.psql_connection_pool import PSQLConnectionPool
from src.template_storage.app.template_storage_app_svc_settings import TemplateStorageAppSettings
from src.template_storage.app.template_manager import TemplateManager


class TemplateStorageApp(AppSvc):

    _outgoing_commands = {
        "created": "template.created",
        "mayUpdate": "template.mayUpdate",
        "updating": "template.updating",
        "updated": "template.updated",
        "mayDelete": "template.mayDelete",
        "deleting": "template.deleting",
        "deleted": "template.deleted"
    }

    def __init__(self, settings: TemplateStorageAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.psql_connection_pool = PSQLConnectionPool()
    
    def _set_incoming_commands(self) -> dict:
        return {
            "template.create": self._create,
            "template.read": self._read,
            "template.update": self._update,
            "template.delete": self._delete,
            "template.read_all": self._read_all,
            "template.read_schemas": self._read_schemas,
        }

    @AppSvc.set_signals(before="template.read.start", after="template.read.end")
    async def _read(self, mes) -> dict:
        template_id = mes.get('data')
        with self.psql_connection_pool.connect() as conn:
            template_manager = TemplateManager(logger=self._logger, psql_connection=conn)
            template = template_manager.get(template_id=template_id)
            if template:
                inner_template = template.get('template')
                processed_template = TemplateRead.model_validate(inner_template)
                return processed_template.model_dump()
            else:
                return {"error": {"code": "404", "message": f"Template {template_id} not found"}}
            
    @AppSvc.set_signals(before="template.read_all.start", after="template.read_all.end")
    async def _read_all(self, mes) -> dict:
        with self.psql_connection_pool.connect() as conn:
            template_manager = TemplateManager(logger=self._logger, psql_connection=conn)
            templates_all = template_manager.get_all()
            if len(templates_all) > 0:
                templates_processed_all = []
                for template_row in templates_all:
                    template_id = template_row[0]
                    templates_processed_all.append({"id": template_id})
                return templates_processed_all
            else:
                return {"error": {"code": "404", "message": f"No templates found"}}
    
    @AppSvc.set_signals(before="template.read_schemas.start", after="template.read_schemas.end")
    async def _read_schemas(self, mes) -> dict:
        template_id = mes.get('data')
        with self.psql_connection_pool.connect() as conn:
            template_manager = TemplateManager(logger=self._logger, psql_connection=conn)
            template_schemas = template_manager.get_schemas(template_id)
            if template_schemas:
                template_schemas_processed = []
                for schema_row in template_schemas:
                    schema_id = schema_row[0]
                    template_schemas_processed.append({"id": schema_id})
                return template_schemas_processed
            else:
                return {"error": {"code": "404", "message": f"No template schemas found"}}

    async def _create(self, mes) -> dict:
        template = mes.get('data')
        try:
            template_valid = TemplateInDB.model_validate(template)
        except BaseException as e:
            return {"error"}
        with self.psql_connection_pool.connect() as conn:
            template_manager = TemplateManager(logger=self._logger, psql_connection=conn)
            template_uuid = template_manager.save(template=template_valid)
            if template_uuid:
                return {"id": template_uuid}
            else:
                return {"error": "Insertion error"}

    async def _delete(self, mes) -> bool:
        template_uuid = mes.get('data')
        with self.psql_connection_pool.connect() as conn:
            template_manager = TemplateManager(logger=self._logger, psql_connection=conn)
            deleted_template_uuid = template_manager.delete(template_id=template_uuid)
            if deleted_template_uuid:
                return {"id": template_uuid}
            else:
                return {"error": f"Template {template_uuid} not found"}

    async def _update(self, mes) -> dict:
        pass

    async def on_startup(self) -> None:
        await super().on_startup()
        self.psql_connection_pool.create_pool()
        
    async def on_shutdown(self) -> None:
        await super().on_shutdown()
        self.psql_connection_pool.close_pool()
    
settings = TemplateStorageAppSettings()

app = TemplateStorageApp(settings=settings, title="`TemplateStorageApp` service")
