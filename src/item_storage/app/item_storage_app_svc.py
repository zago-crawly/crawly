import asyncio
import os
import json
import sys
from typing import MutableMapping
import aio_pika
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(".")
from src.common.app_svc import AppSvc
from src.item_storage.app.item_storage_app_svc_settings import ItemStorageAppSettings


class ItemStorageApp(AppSvc):

    _outgoing_commands = {
        "created": "schema.created",
        "mayUpdate": "schema.mayUpdate",
        "updating": "schema.updating",
        "updated": "schema.updated",
        "mayDelete": "schema.mayDelete",
        "deleting": "schema.deleting",
        "deleted": "schema.deleted"
    }

    def __init__(self, settings: ItemStorageAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.mongo_client = AsyncIOMotorClient(os.environ.get('MONGO_URI'))

    def _set_incoming_commands(self) -> dict:
        return {
            "item.read": self._read,
            "item.search": self._search,
        }

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()
        
    async def _read(self, mes) -> dict:
        data = mes.get('data')
        collection_id = data.get('task_id')
        skip = data.get('skip')
        limit = data.get('limit')
        db = self.mongo_client[os.environ.get('MONGO_DB')]
        res = []
        async for document in db[collection_id].find({}).skip(skip).limit(limit):
            document['_id'] = str(document.get('_id'))
            res.append(document)
        return res

    async def _search(self, mes) -> dict:
        collection_id = mes.get('collection_id')
        text = mes.get('text')
        limit = mes.get('limit')
        self._logger.info(collection_id)
        db = self.mongo_client[settings.mongo_db_main_db_name]
        cursor = await db[collection_id].find({"$text": {"$search": text}})
        result = []
        if limit: 
            cursor.limit(limit)
        async for document in cursor.to_list():
            result.append(document)
        return result
        
    async def on_startup(self) -> None:
        await super().on_startup()

settings = ItemStorageAppSettings()

app = ItemStorageApp(settings=settings, title="`ItemStorageApp` service")
