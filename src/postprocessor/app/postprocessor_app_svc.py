import sys
import os
import asyncio
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
        # self.client = pymongo.MongoClient(self.mongo_uri)
        # self.task_broker = AioPikaBroker(self._conf.amqp_url)
    
    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    def _set_incoming_commands(self) -> dict:
        return {
        }

    async def signal_processor(self, mes):
        
        self._logger.error(mes)

    # @AppSvc.set_signals(before="postprocessor.process.start", after="postprocessor.process.end")
    async def _process(self, mes) -> dict:
        self._logger.error(mes)
        # task = None # TODO Get task from incoming message
        # schema_uuid = None # TODO Get schema_uuid from incoming task
        # db = self.client[self.mongo_db] # Get db by template_uuid
        # schema = await self._post_message(
        #         mes={"action": "schema.read", "data": schema_uuid}, reply=True
        #     )
        # if schema.get('error'):
        #     return
        # template_uuid = await self._post_message(
        #         mes={"action": "schema.get_template_by_schema", "data": schema_uuid}, reply=True
        #     )
        # if template_uuid.get('error'):
        #     return
        # # data_pipeline = Pipeline([ProcessString, ProcessTime, Translate, Geocode])
        return 

    async def on_startup(self) -> None:
        # await self.task_broker.startup()
        # self.postprocess_task = self.task_broker.register_task(self.postprocess, task_name="postprocess")
        # self.worker_task = asyncio.create_task(run_receiver_task(self.task_broker))
        # self._logger.error("created worker")
        # self._logger.error("created task")
        await super().on_startup()
        
    async def on_shutdown(self):
        # self.worker_task.cancel()
        # await self.task_broker.shutdown()
        return await super().on_shutdown()
    
settings = PostprocessorAppSettings()

app = PostprocessorApp(settings=settings, title="`PostprocessorApp` service")
