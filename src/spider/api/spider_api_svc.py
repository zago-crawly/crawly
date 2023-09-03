import asyncio
import json
import sys
import os
from typing import MutableMapping
import aio_pika
from concurrent.futures import ProcessPoolExecutor
import subprocess

sys.path.append(".")
from src.common.base_svc import BaseSvc
from src.spider.api.spider_api_svc_settings import SpiderAPISettings
from src.common.models.task import TaskForSpider


class SpiderAPI(BaseSvc):

    def __init__(self, settings: SpiderAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()
        
        for key, item in self._config.subscribe.items():
            self._amqp_subscribe[key] = {
                "publish": {},
                "consume": {}
            }

            # сюда будем публиковать заявки на уведомления
            self._amqp_subscribe[key]["publish"]["exchange"] = \
                await self._amqp_channel.declare_exchange(
                    item["publish"]["name"], item["publish"]["type"], durable=True
            )
            self._amqp_subscribe[key]["publish"]["routing_key"] = \
                item["publish"]["routing_key"]

            # для получения уведомлений подсоединим свою главную очередь
            self._amqp_subscribe[key]["consume"]["exchange"] = \
                await self._amqp_channel.declare_exchange(
                    item["consume"]["name"], item["consume"]["type"], durable=True
            )
            await self._amqp_consume["queue"].bind(
                exchange=self._amqp_subscribe[key]["consume"]["exchange"],
                routing_key=self._amqp_subscribe[key]["consume"]["routing_key"]
            )

    def _set_incoming_commands(self) -> dict:
        return {
            "spider.start": self._start,
        }

    async def _start(self, mes):
        new_task = TaskForSpider.model_validate(mes.get('data'))
        self._logger.error(new_task)
        subprocess.call([f"{sys.executable}", "-m", "scrapy", "runspider", f"{os.environ.get('SPIDER_SCRIPT_DIR')}/spider.py", "-a", f"task={new_task.model_dump_json(by_alias=True)}"], shell=False)

    async def on_startup(self) -> None:
        await super().on_startup()

settings = SpiderAPISettings()

app = SpiderAPI(settings=settings, title="`SpiderAPI` service")

@app.get("/run_spider/{spider_name}")
async def run_spider(spider_name: str):
    return {"message": f"Running spider: {spider_name}"}