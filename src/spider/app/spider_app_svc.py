import sys
import logging
from crochet import setup

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

sys.path.append(".")
from src.spider.app.spiders.spider import Spider
from src.common.app_svc import AppSvc
from src.spider.app.spider_app_svc_settings import SpiderAppSettings
from src.common.models.task import TaskForSpider


class SpiderApp(AppSvc):

    setup()

    def __init__(self, settings: SpiderAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.spider_settings = get_project_settings()

    def _set_incoming_commands(self) -> dict:
        return {
            "spider.start": self._start,
        }
            
    @AppSvc.set_signals(before="spider.start", after="spider.stop", path_to_obj_id="data.template_uuid")
    async def _start(self, mes: dict):
        task = TaskForSpider.model_validate(mes.get('data'))
        spider_id = task.task_uuid
        self._logger.error(f"spider {spider_id} started")
        runner = CrawlerRunner(self.spider_settings)
        runner.crawl(Spider, task)
        self._logger.error(f"spider {spider_id} ended")
        return task.schema_uuid
                          
    async def on_startup(self) -> None:
        logging.getLogger('scrapy').setLevel('ERROR')
        await super().on_startup()

settings = SpiderAppSettings()

app = SpiderApp(settings=settings, title="`SpiderApp` service")
