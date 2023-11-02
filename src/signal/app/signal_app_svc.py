import asyncio
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
        signal_data = mes.get("data")
        self._logger.error(signal_route, signal_data.get('id'))
        await self._signals_exchange.publish(
        message=aio_pika.Message(
            body=json.dumps(signal_data, ensure_ascii=False).encode(),
        ), routing_key=signal_route)
        return
    
    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process(ignore_processed=True):
            mes = json.loads(message.body.decode())
            await self.route_mes(mes)
            await message.ack()

    async def _connect_to_signal_exchange(self):
        connected = False
        while not connected:
            try:
                self._logger.info("Создание очереди для передачи сигналов от сервисов...")

                self._signals_channel = await self._amqp_connection.channel()
                self._signals_exchange = await self._signals_channel.declare_exchange("signals", aio_pika.ExchangeType.TOPIC, durable=True)

                connected = True

                self._logger.info("Создание очереди для передачи сигналов завершено.")

            except aio_pika.AMQPException as ex:
                self._logger.error(f"Ошибка связи с брокером: {ex}")
                await asyncio.sleep(5)
        return

    async def _disconnect_from_signal_exchange(self):
        await self._signals_channel.close()

    async def on_startup(self) -> None:
        await super().on_startup()
        await self._connect_to_signal_exchange()
        
    async def on_shutdown(self) -> None:
        await super().on_shutdown()
        await self._disconnect_from_signal_exchange()
    
settings = SignalAppSettings()

app = SignalApp(settings=settings, title="`SignalApp` service")
