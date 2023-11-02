import sys
from fastapi import APIRouter, Response, HTTPException

sys.path.append(".")
from src.common.models.schema import SchemaCreate
from src.schema_storage.api.schema_storage_api_svc_settings import SchemaStorageAPISettings
from src.common.api_svc import APISvc


class SchemaStorageAPI(APISvc):

    _outgoing_commands = {
        "create": "schema.create",
        "read": "schema.read",
        "update": "schema.update",
        "delete": "schema.delete"
    }

    def __init__(self, settings: SchemaStorageAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def create(self, payload: SchemaCreate) -> dict:
        return await super().create(payload=payload.model_dump(by_alias=True))

    async def read(self, schema_id: str) -> dict:
        return await super().read(payload=schema_id)
        
    async def get_template_by_schema(self, schema_id: str) -> dict:
        body = {
         "action": "schema.get_template_by_schema",
         "data": schema_id  
        }
        return await self._post_message(mes=body, reply=True)
        
    async def delete(self, schema_id: str) -> dict:
        return await super().delete(payload=schema_id)
    
    # async def update(self, template_id, payload) -> dict:
    #     body = {
    #         "action": "update",
    #         "task_id": template_id,
    #         "body": payload.dict()
    #     }
    #     return await self._post_message(mes=body, reply=True)

settings = SchemaStorageAPISettings()

app = SchemaStorageAPI(docs_url="/schema_storage", redoc_url=None, settings=settings, title="Schema storage API service")

router = APIRouter(tags=['Schema'])


@router.post("/",
             response_model={},
             status_code=201)
async def create(payload: SchemaCreate):
    return await app.create(payload)

@router.get("/{schema_id}",
            response_model={},
            status_code=200)
async def read(schema_id: str):
    res = await app.read(schema_id)
    return res

@router.get("/{schema_id}/template", status_code=200)
async def get_template_by_schema(schema_id: str):
    res = await app.get_template_by_schema(schema_id)
    return res

# @router.delete("/{schema_id}")
# async def read(schema_id: str):
#     res = await app.delete(schema_id)
#     if res:
#         return Response(status_code=204)
#     return HTTPException(status_code=404)

# @router.put("/task/{task_id}",
#             response_model=TaskPartialUpdateResult,
#             status_code=200)
# async def update(task_id: str, payload: TaskPartialUpdate):
#     res = await app.update(task_id, payload)
#     app._logger.info(res)
#     return res

app.include_router(router, prefix=f"/schema_storage")

