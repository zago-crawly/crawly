"""
Модуль содержит классы, описывающие форматы входных данных для команд,
а также класс APICRUDSvc - базовый класс для всех сервисов
<сущность>_api_crud.
"""
import sys
from fastapi import APIRouter, Response, HTTPException

sys.path.append(".")
from src.common.models.task import (TaskCreate,
                                    TaskRead,
                                    TaskUpdate,
                                    TaskUpdateResult)
from src.scheduler.api.scheduler_api_svc_settings import SchedulerAPISettings
from src.common.api_svc import APISvc


class SchedulerAPI(APISvc):

    _outgoing_commands = {
        "create": "task.create",
        "read": "task.read",
        "read_all": "task.read_all",
        # "read": "task.read",
        # "read": "task.read",
        "update": "task.update",
        "delete": "task.delete",
        "pause": "task.pause",
        "resume": "task.resume"
    }

    def __init__(self, settings: SchedulerAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def create(self, payload: TaskCreate) -> dict:
        return await super().create(payload=payload.model_dump())

    async def delete(self, task_id: str) -> dict:
        return await super().delete(payload=task_id)

    async def read(self, task_id: str) -> dict:
        return await super().read(payload=task_id)

    async def read_all(self) -> dict:
        body = {
            "action": self._outgoing_commands["read_all"],
            "data": ""
        }
        return await self._post_message(mes=body, reply=True)

    async def read_by_schema(self, task_id: str) -> dict:
        return await super().read(payload=task_id)

    async def read_by_template(self, task_id: str) -> dict:
        return await super().read(payload=task_id)

    async def resume(self, task_id: str) -> bool:
        body = {
            "action": self._outgoing_commands["resume"],
            "data": task_id
        }
        return await self._post_message(mes=body, reply=True)

    async def pause(self, task_id: str) -> bool:
        body = {
            "action": self._outgoing_commands["pause"],
            "data": task_id
        }
        return await self._post_message(mes=body, reply=True)

    async def update(self, payload: TaskUpdate) -> dict:
        return await super().update(payload=payload.model_dump())


settings = SchedulerAPISettings()

app = SchedulerAPI(docs_url="/scheduler", redoc_url=None, settings=settings, title="Scheduler API service")

router = APIRouter(tags=['Task'])


@router.post("/tasks",
             response_model=dict,
             status_code=201)
async def create(payload: TaskCreate):
    return await app.create(payload)


@router.get("/tasks/{task_id}",
            response_model=TaskRead,
            status_code=200)
async def read(task_id: str):
    res = await app.read(task_id)
    app._logger.info(res)
    try:
        model = TaskRead.model_validate(res)
        app._logger.error(model)
    except BaseException as e:
        app._logger.error(e)
    return res


@router.get("/tasks",
            status_code=200)
async def read_all():
    res = await app.read_all()
    return res


@router.get("/tasks/{task_id}/pause")
async def pause(task_id: str):
    res = await app.pause(task_id)
    if res:
        return Response(status_code=200)
    return HTTPException(status_code=404)


@router.get("/tasks/{task_id}/resume")
async def resume(task_id: str):
    res = await app.resume(task_id)
    if res:
        return Response(status_code=200)
    return HTTPException(status_code=404)


@router.delete("/tasks/{task_id}")
async def delete(task_id: str):
    res = await app.delete(task_id)
    if res:
        return Response(status_code=204)
    return HTTPException(status_code=404)


@router.put("/tasks/{task_id}",
            response_model=TaskUpdateResult,
            status_code=200)
async def update(task_id: str, payload: TaskUpdate):
    payload.task_uuid = task_id
    return await app.update(payload)

app.include_router(router, prefix="/scheduler")
