import sys
import os
import subprocess
from queue import Queue
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List

sys.path.append(".")
from src.common.app_svc import AppSvc
from src.spider.app.spider_app_svc_settings import SpiderAppSettings
from src.common.models.task import TaskForSpider


class SpiderApp(AppSvc):

    def __init__(self, settings: SpiderAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.task_queue = Queue()

    def _set_incoming_commands(self) -> dict:
        return {
            "spider.start": self._start,
        }        

    def task_queue_maintenance(self):
        task_batch_size = min(self.task_queue.qsize(), 5)
        if task_batch_size > 0:
            task_batch = []
            for _ in range(task_batch_size):
                task_batch.append(self.task_queue.get())
            self.run_spiders(tasks=task_batch)
            
    async def run_spider_batch(self, tasks: List[TaskForSpider]):
        proc_list = []
        for task in tasks:
            spider_id = task.task_uuid
            await self._post_message(mes={"action": "signal.spider.start", "data": spider_id})
            self._logger.error(f"spider {spider_id} started")
            process = subprocess.Popen([f"{sys.executable}",
                                        "-m",
                                        "scrapy",
                                        "runspider",
                                        f"{os.environ.get('SPIDER_SCRIPT_DIR')}/spider.py",
                                        "-a",
                                        f"task={task.model_dump_json(by_alias=True)}"],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL,
                                        shell=False)
            proc_list.append((spider_id, process))
            await self._post_message(mes={"action": "signal.spider.closed", "data": spider_id})
        for spider_id, proc in proc_list:
            proc.wait()
            self._logger.error(f"spider {spider_id} ended")
                  
    async def _start(self, mes):
        new_task = TaskForSpider.model_validate(mes.get('data'))
        self.task_queue.put(new_task)
            
    async def on_startup(self) -> None:
        await super().on_startup()
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.task_queue_maintenance, 'cron', minute="*")
        scheduler.start()

settings = SpiderAppSettings()

app = SpiderApp(settings=settings, title="`SpiderApp` service")
