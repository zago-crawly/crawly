import json
import sys
from pydantic import BaseModel
from typing import Any
import aio_pika
import aio_pika.abc


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.signal.app_api.signal_app_api_svc_settings import SignalAppAPISettings

class Signal(BaseModel):
    signal: str
    data: dict | str

class SignalAppAPI(AppSvc):

    def __init__(self, settings: SignalAppAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        
    def _set_incoming_commands(self) -> dict:
        return {}

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> Any:
        async with message.process(ignore_processed=True):
            mes = message.body.decode()

            try:
                mes = json.loads(mes)
            except json.decoder.JSONDecodeError:
                self._logger.error(f"Сообщение {mes} не в формате json.")
                await message.ack()
                return
            
            reject = await self._reject_message(mes)
            if reject:
                await message.reject(True)
                return
                        
            try:
                validated_signal = Signal.model_validate_json(mes)
                await self._post_message(mes=validated_signal.model_dump())
                self._logger.info(validated_signal)
            except ValueError as e:
                self._logger.error(f"Неверный формат сигнала")
                self._logger.error(e)
                await message.ack()
                return

            await message.ack()
        
    async def on_startup(self) -> None:
        await super().on_startup()
        
    async def on_shutdown(self) -> None:
        await super().on_shutdown()
    
settings = SignalAppAPISettings()

app = SignalAppAPI(settings=settings, title="`SignalAppAPI` service")