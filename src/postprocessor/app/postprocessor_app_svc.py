import asyncio
import sys
import os
import pymongo
from fastcore.transform import Pipeline


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.postprocessor.app.postprocessor_app_svc_settings import PostprocessorAppSettings
from src.postprocessor.pipeline.geocode import Geocode
from src.postprocessor.pipeline.process_string import ProcessString
from src.postprocessor.pipeline.translate import Translate
from src.postprocessor.pipeline.process_time import ProcessTime


class PostprocessorApp(AppSvc):

    def __init__(self, settings: PostprocessorAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.mongo_uri=os.environ.get('MONGO_URI')
        self.mongo_db=os.environ.get('MONGO_DB')
        self.client = pymongo.MongoClient(self.mongo_uri)
    
    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    def _set_incoming_commands(self) -> dict:
        return {
        }

    @AppSvc.set_signals(before="postprocessor.process.start", after="postprocessor.process.end")
    async def _process(self, mes) -> dict:
        task = None # TODO Get task from incoming message
        schema_uuid = None # TODO Get schema_uuid from incoming task
        db = self.client[self.mongo_db] # Get db by template_uuid
        schema = await self._post_message(
                mes={"action": "schema.read", "data": schema_uuid}, reply=True
            )
        self._logger.error(schema)
        if schema.get('error'):
            return schema
        data_pipeline = Pipeline([ProcessString, ProcessTime, Translate, Geocode])
        return 

    async def on_startup(self) -> None:
        await super().on_startup()

    
settings = SchedulerAppSettings()

app = SchedulerApp(settings=settings, title="`SchedulerApp` service")
