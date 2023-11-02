import sys
import os
import subprocess
import asyncio

sys.path.append(".")
from src.common.app_svc import AppSvc
from src.spider.app.spider_app_svc_settings import SpiderAppSettings
from src.common.models.task import TaskForSpider


class SpiderApp(AppSvc):

    def __init__(self, settings: SpiderAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    def _set_incoming_commands(self) -> dict:
        return {
            "spider.start": self._start,
        }
            
    @AppSvc.set_signals(before="spider.start", after="spider.stop", path_to_obj_id="data.template_uuid")
    async def _start(self, mes: dict):
        task = TaskForSpider.model_validate(mes.get('data'))
        spider_id = task.task_uuid
        self._logger.error(f"spider {spider_id} started")
        subprocess.call([f"{sys.executable}", "-m", "scrapy", "runspider", f"{os.environ.get('SPIDER_SCRIPT_DIR')}/spider.py", "-a", f"task={task.model_dump_json(by_alias=True)}"], shell=False)
        self._logger.error(f"spider {spider_id} ended")
        return task.schema_uuid
                          
    async def on_startup(self) -> None:
        await super().on_startup()

settings = SpiderAppSettings()

app = SpiderApp(settings=settings, title="`SpiderApp` service")
