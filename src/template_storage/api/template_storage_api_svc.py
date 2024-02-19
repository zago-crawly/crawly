import json
import sys
from typing import Dict, List
from fastapi import APIRouter, Request, Response, HTTPException

sys.path.append(".")
from src.common.models.template import TemplateCreate, TemplateRead
from src.template_storage.api.template_storage_api_svc_settings import TemplateStorageAPISettings
from src.common.api_svc import APISvc


class TemplateStorageAPI(APISvc):

    def __init__(self, settings: TemplateStorageAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    _outgoing_commands = {
        "create": "template.create",
        "read": "template.read",
        "update": "template.update",
        "delete": "template.delete",
        "read_all": "template.read_all",
        "read_schemas": "template.read_schemas",
    }

    async def create(self, payload: TemplateCreate) -> dict:
        return await super().create(payload=payload)

    async def read(self, template_id: str) -> dict:
        return await super().read(payload=template_id)
    
    async def read_all(self) -> dict:
        body = {
            "action": self._outgoing_commands["read_all"],
            "data": ""
        }
        return await self._post_message(mes=body, reply=True)

    async def read_schemas(self, template_id: str) -> dict:
        body = {
            "action": self._outgoing_commands["read_schemas"],
            "data": template_id
        }
        return await self._post_message(mes=body, reply=True)

    async def delete(self, template_id: str) -> dict:
        return await super().delete(payload=template_id)

settings = TemplateStorageAPISettings()

app = TemplateStorageAPI(settings=settings, title="Template storage API service")


router = APIRouter(tags=['Template'])

@router.post("/templates", response_model={}, status_code=201)
async def create(payload: TemplateCreate):
    app._logger.error(payload)
    return await app.create(payload.model_dump())

@router.get("/templates/{template_id}",
            response_model=TemplateRead,
            status_code=200)
async def read(template_id: str):
    res = await app.read(template_id)
    return res

@router.get("/templates/{template_id}/schemas")
async def read_schemas(template_id: str):
    res = await app.read_schemas(template_id)
    return res
    
@router.delete("/templates/{template_id}")
async def delete(template_id: str):
    res = await app.delete(template_id)
    app._logger.info(res)
    if res.get("id"):
        return Response(status_code=204)
    return Response(json.dumps(res), status_code=404)

@router.get("/templates",
            response_model=List[Dict[str, str]],
            status_code=200)
async def read_all():
    res = await app.read_all()
    return res

app.include_router(router, prefix="/template_storage")