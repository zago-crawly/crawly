import sys
import asyncio
from collections.abc import MutableMapping
from typing import Optional
import aio_pika.abc
from fastapi import APIRouter, Query, HTTPException
# from fastapi.responses import JSONResponse

sys.path.append(".")
from src.common.api_svc import APISvc
from src.item_storage.api.item_storage_api_svc_settings import ItemStorageAPISettings


class MongostorageAPI(APISvc):

    _outgoing_commands = {
        "read": "item.read",
        "search": "item.search"
    }

    def __init__(self, settings: ItemStorageAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    async def read(self,
                   task_id: str,
                   skip: int = 0,
                   limit: int = 10) -> dict:
        body = {
            "task_id": task_id,
            "skip": skip,
            "limit": limit
        }
        return await super().read(payload=body)
    
    async def _search(self,
                     task_id: str,
                     text: str):
        body = {
            "action": "item.search",
            "task_id": task_id,
            "text": text
        }
        return await self._post_message(mes=body, reply=True)
        
    async def create(self) -> dict:
        return
        
    async def delete(self) -> dict:
        return 

settings = ItemStorageAPISettings()

app = MongostorageAPI(settings=settings, title="`ItemStorageAPI` service")

router = APIRouter()

@router.get("/{task_id}")
async def read_limit(task_id: str,
                    skip: int = Query(0, description="Start item to return"),
                    limit: int = Query(10, description="Number of items to return")):
    items = await app.read(task_id, skip, limit)
    if items:
        return items
    return HTTPException(status_code=404)

@router.get("")
async def search(collection_id: str,
                 text: str):
    items = await app.search(collection_id, text)
    if items: 
        return items
    else:
        return HTTPException(status_code=404)

app.include_router(router, prefix=f"/item_storage", tags=["storage", "item_torage"])