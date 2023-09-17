import asyncio
import json
import sys
from typing import Any
import aio_pika
import aio_pika.abc


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.signal.app_api.signal_app_api_svc_settings import SignalAppAPISettings


class SignalAppAPI(AppSvc):

    # _outgoing_commands = {
    #     "created": "template.created",
    #     "mayUpdate": "template.mayUpdate",
    #     "updating": "template.updating",
    #     "updated": "template.updated",
    #     "mayDelete": "template.mayDelete",
    #     "deleting": "template.deleting",
    #     "deleted": "template.deleted"
    # }

    def __init__(self, settings: SignalAppAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        
    def _set_incoming_commands(self) -> dict:
        return {
            "template.create": self._create,
            "template.read": self._read,
            "template.update": self._update,
            "template.delete": self._delete,
        }

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> Any:
        print(message)
        return await super()._process_message(message)

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
    
settings = SignalAppAPISettings()

app = SignalAppAPI(settings=settings, title="`SignalAppAPI` service")
