"""
Модуль содержит классы, описывающие форматы входных данных для команд,
а также класс APICRUDSvc - базовый класс для всех сервисов
<сущность>_api_crud.
"""
import sys
import asyncio
import json
from typing import List
from collections.abc import MutableMapping
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, Json
from aio_pika import Message
import aio_pika.abc
from fastapi import APIRouter

sys.path.append(".")
from common.models.task import TaskCreate, TaskCreateResult
from src.scheduler.api.scheduler_api_svc_settings import SchedulerAPISettings
from src.common.api_svc import Svc


class SchedulerAPI(Svc):

    def __init__(self, settings: SchedulerAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

        self.api_version = settings.api_version
        self._callback_futures: MutableMapping[str, asyncio.Future] = {}

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    async def create(self, payload: TaskCreate) -> dict:
        body = {
            "action": "create",
            "data": payload.dict()
        }
        print(body)
        return await self._post_message(mes=body, reply=True)


settings = SchedulerAPISettings()

app = SchedulerAPI(settings=settings, title="`SchedulerAPI` service")

router = APIRouter()


@router.post("/",
             # response_model=TaskCreateResult,
             status_code=201)
async def create(payload: TaskCreate):
    return await app.create(payload)

# @router.get("/", response_model=svc.NodeCreateResult, status_code=200)
# async def read(payload: TagRead):
#     return await app.create(payload)


app.include_router(router, prefix=f"{settings.api_version}/scheduler", tags=["scheduler"])
