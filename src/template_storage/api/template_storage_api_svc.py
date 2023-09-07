import sys
from fastapi import APIRouter, Response, HTTPException

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
        "delete": "template.delete"
    }

    async def create(self, payload: TemplateCreate) -> dict:
        return await super().create(payload=payload)

    async def read(self, template_id: str) -> dict:
        return await super().read(payload=template_id)
        
    async def delete(self, template_id: str) -> dict:
        return await super().delete(payload=template_id)
    
    # async def update(self, template_id, payload) -> dict:
    #     body = {
    #         "action": "update",
    #         "task_id": template_id,
    #         "body": payload.dict()
    #     }
    #     return await self._post_message(mes=body, reply=True)

settings = TemplateStorageAPISettings()

app = TemplateStorageAPI(docs_url="/template_storage", root_path="/template_storage", redoc_url=None, settings=settings, title="Template storage API service")

router = APIRouter(tags=['Template'])


@router.post("/",
             response_model={},
             status_code=201)
async def create(payload: TemplateCreate):
    return await app.create(payload.model_dump())

@router.get("/{template_id}",
            response_model=TemplateRead,
            status_code=200)
async def read(template_id: str):
    res = await app.read(template_id)
    app._logger.error(res)
    return res

@router.delete("/{template_id}")
async def read(template_id: str):
    res = await app.delete(template_id)
    if res:
        return Response(status_code=204)
    return HTTPException(status_code=404)

# @router.put("/task/{task_id}",
#             response_model=TaskPartialUpdateResult,
#             status_code=200)
# async def update(task_id: str, payload: TaskPartialUpdate):
#     res = await app.update(task_id, payload)
#     app._logger.info(res)
#     return res

app.include_router(router, prefix=f"/template_storage")
