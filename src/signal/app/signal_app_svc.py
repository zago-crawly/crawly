import json
import sys
from typing import Any
import aio_pika
import aio_pika.abc
from fastapi import APIRouter


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.signal.app.signal_app_svc_settings import SignalAppSettings


class SignalApp(AppSvc):

    def __init__(self, settings: SignalAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        
    def _set_incoming_commands(self) -> dict:
        return {}

    async def route_mes(self, mes):
        signal_route = mes.get("signal", "anonymous.info")
        obj_id = mes.get("obj_id", "")
        self._logger.error(signal_route, obj_id)
        await self._post_message(mes=obj_id, routing_key=signal_route, reply=False)
        return
    
    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process(ignore_processed=True):
            mes = json.loads(message.body.decode())
            await self.route_mes(mes)
            await message.ack()

    async def on_startup(self) -> None:
        await super().on_startup()
        
    async def on_shutdown(self) -> None:
        await super().on_shutdown()
    
settings = SignalAppSettings()

app = SignalApp(settings=settings, title="`SignalApp` service")
