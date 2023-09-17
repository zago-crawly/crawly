import asyncio
import json
import sys
from typing import MutableMapping
from uuid import uuid4
import aio_pika
from fastapi import APIRouter


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.common.models.template import TemplateInDB, TemplateRead
from src.common.psql_connection_pool import PSQLConnectionPool
from src.signal.app.signal_app_svc_settings import SignalAppSettings


class SignalApp(AppSvc):

    # _outgoing_commands = {
    #     "created": "template.created",
    #     "mayUpdate": "template.mayUpdate",
    #     "updating": "template.updating",
    #     "updated": "template.updated",
    #     "mayDelete": "template.mayDelete",
    #     "deleting": "template.deleting",
    #     "deleted": "template.deleted"
    # }

    def __init__(self, settings: SignalAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.psql_connection_pool = PSQLConnectionPool()
        
    def _set_incoming_commands(self) -> dict:
        return {
            "template.create": self._create,
            "template.read": self._read,
            "template.update": self._update,
            "template.delete": self._delete,
        }
    
    async def _read(self, mes) -> dict:
        pass
        
    async def _create(self, mes) -> dict:
        pass

    async def _delete(self, mes) -> bool:
        pass

    async def _update(self, mes) -> dict:
        pass

    async def on_startup(self) -> None:
        await super().on_startup()
        
    async def on_shutdown(self) -> None:
        await super().on_shutdown()
    
settings = SignalAppSettings()

app = SignalApp(settings=settings, title="`SignalApp` service")
