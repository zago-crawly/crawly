import sys
import os
import asyncio
import pymongo
from fastcore.transform import Pipeline

sys.path.append(".")
from src.postprocessor.pipeline.models import PipelineError, SchemaBlockField
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
        self.db = self.client[self.mongo_db]
        self.schema = {}
        self.flat_schema = {}
        self.data_pipeline = Pipeline([
            ProcessString,
            # ProcessTime,
            # Translate,
            # Geocode
            ])
    
    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    def _set_incoming_commands(self) -> dict:
        return {
        }

    @AppSvc.set_signals(before="postprocessor.process.start", after="postprocessor.process.end")
    async def signal_processor(self, mes):
        template_uuid = mes.get('id')
        schema_uuid = mes.get('data')
        await self.get_schema(schema_uuid=schema_uuid)
        self.flatten_schema()
        self._logger.info(self.flat_schema)
        unprocessed_data = await self.get_unprocessed_items(collection=template_uuid, schema_uuid=schema_uuid)
        for item in unprocessed_data:
            item_id = item['_id']
            new_item = {"__schema_uuid": schema_uuid}
            for field_name, field in self.flat_schema.items():
                self._logger.info(field)
                field_model = SchemaBlockField(
                    field_name=field_name,
                    field_processors=field.get('postprocessors'),
                    output_field=item.get(field_name),
                )
                processed_field: SchemaBlockField | PipelineError = self.data_pipeline(field_model)
                if isinstance(processed_field, PipelineError):
                    continue
                new_item[field_name] = processed_field.output_field
            await self.save_processed_item(template_uuid, new_item)
            await self.mark_processed(template_uuid, item_id)
        return         

    async def get_unprocessed_items(self, collection: str, schema_uuid: str):
        item_collection = self.db[collection]
        unprocessed_items = []
        cursor = item_collection.find({"__processed": False, "__schema_uuid": schema_uuid}, {"__processed": 0, "__hash": 0, "__schema_uuid": 0})
        for item in cursor:
            unprocessed_items.append(item)
        return unprocessed_items

    async def mark_processed(self, collection: str, item_id: str):
        self.db[collection].find_one_and_update({"_id": item_id}, {"$set": {"__processed": True}})
        return

    async def save_processed_item(self, template_uuid: str, item: dict):
        processed_collection_name = f"proc_{template_uuid}"
        self.db[processed_collection_name].insert_one(item)
        return

    async def get_schema(self, schema_uuid: str):
        resp = await self._post_message(
                mes={"action": "schema.read", "data": schema_uuid}, reply=True
            )
        if resp.get('error'):
            return
        schema, _ = resp.values()
        self.schema = schema

    def flatten_schema(self):
        for schema_block_name, schema_block in self.schema.items():
            for schema_field_name, schema_field in schema_block.items():
                if not schema_field:
                    continue
                self.flat_schema[schema_field_name] = schema_field
        return

    async def process_field(self, schema_block_field: dict, pipeline):
        processed_field: SchemaBlockField | PipelineError = pipeline(schema_block_field)
        return

    async def save_processed_field(self, processed_field: SchemaBlockField):
        return

    async def on_startup(self) -> None:
        await super().on_startup()
        
    async def on_shutdown(self):
        return await super().on_shutdown()
    
settings = PostprocessorAppSettings()

app = PostprocessorApp(settings=settings, title="`PostprocessorApp` service")
