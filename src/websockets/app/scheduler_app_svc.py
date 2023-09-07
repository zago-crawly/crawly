import asyncio
import json
import sys
from typing import MutableMapping
import aio_pika
from fastapi import APIRouter
from pytz import utc
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler


sys.path.append(".")
from src.common.api_svc import Svc
from src.scheduler.app.scheduler_job_send_message import job_send_message
from src.scheduler.app.scheduler_app_svc_settings import SchedulerAppSettings
from src.scheduler.app.scheduler_conf import (
    jobstores,
    # executors,
    job_defaults)


class SchedulerApp(Svc):

    def __init__(self, settings: SchedulerAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

        self.api_version = settings.api_version
        self._callback_futures: MutableMapping[str, asyncio.Future] = {}

        self.scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop(),
                                          jobstores=jobstores,
                                        #   executors=executors,
                                          job_defaults=job_defaults,
                                          timezone=utc)

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    async def _process_message(
            self,
            message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        """Метод обработки сообщений от сервиса ``scheduler_api``.

        Сообщения должны приходить в формате:

        .. code:: json

            {
                "action": "create | read | update | delete",
                "data: {}
            }

        где

        * **action** - команда ("create", "read", "update", "delete"), при
          этом строчные или прописные буквы - не важно;
        * **data** - параметры команды.

        После выполнения соответствующей команды входное сообщение квитируется
        (``messsage.ack()``).

        В случае, если в сообщении установлен параметр ``reply_to``,
        то квитирование происходит после публикации ответного сообщения в
        очередь, указанную в ``reply_to``.

        """
        async with message.process(ignore_processed=True):
            mes = message.body.decode()
            try:
                mes = json.loads(mes)
            except json.decoder.JSONDecodeError:
                self._logger.error(f"Сообщение {mes} не в формате json.")
                await message.ack()
                return

            action = mes.get("action")
            if not action:
                self._logger.error(f"В сообщении {mes} не указано действие.")
                await message.ack()
                return

            action = action.lower()
            if action == "create":
                res = await self._create(mes)
            # elif action == "update":
            #     res = await self._update(mes)
            # elif action == "read":
            #     res = await self._read(mes)
            # elif action == "delete":
            #     res = await self._delete(mes)
            else:
                self._logger.error(f"Неизвестное действие: {action}.")
                await message.ack()
                return

            if not message.reply_to:
                await message.ack()
                return

            await self._amqp_consume["main"]["exchange"].publish(
                aio_pika.Message(
                    body=json.dumps(res, ensure_ascii=False).encode(),
                    correlation_id=message.correlation_id,
                ),
                routing_key=message.reply_to,
            )
            await message.ack()

    async def _create(self, mes):
        cron = mes.get('data').get('cron')
        resource_name = mes.get('data').get('resource_name')
        body = json.dumps(mes, ensure_ascii=False).encode()
        if cron:
            publish_exchange = self._config.publish["main"]
            self.scheduler.add_job(job_send_message,
                                   CronTrigger.from_crontab(cron),
                                   kwargs={"amqp_url": self._config.amqp_url,
                                           "exchange_name": publish_exchange["name"],
                                           "body": body,
                                           "routing_key": publish_exchange["routing_key"] 
                                           },
                                   )
            self._logger.info(f'Создано задание для парсинга ресурса {resource_name} с расписанием {cron}')
        else:
            self._logger.error(f"В сообщении отсутствует параметр cron (расписание)")
            return

    async def on_startup(self) -> None:
        await super().on_startup()
        self.scheduler.start()

    
settings = SchedulerAppSettings()

app = SchedulerApp(settings=settings, title="`SchedulerApp` service")
