import sys
import os
import subprocess

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

    async def _start(self, mes):
        self._logger.error(mes)
        new_task = TaskForSpider.model_validate(mes.get('data'))
        subprocess.call([f"{sys.executable}", "-m", "scrapy", "runspider", f"{os.environ.get('SPIDER_SCRIPT_DIR')}/spider.py", "-a", f"task={new_task.model_dump_json(by_alias=True)}"], shell=False)

    async def on_startup(self) -> None:
        await super().on_startup()

settings = SpiderAppSettings()

app = SpiderApp(settings=settings, title="`SpiderApp` service")

# @app.get("/run_spider/{spider_name}")
# async def run_spider(spider_name: str):
#     return {"message": f"Running spider: {spider_name}"}