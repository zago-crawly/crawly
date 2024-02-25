import asyncio
import sys
from typing import List
from uuid import uuid4
from pytz import utc
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

sys.path.append(".")
from src.common.app_svc import AppSvc
from src.scheduler.app.scheduler_job_send_message import job_send_message
from src.scheduler.app.scheduler_app_svc_settings import SchedulerAppSettings
from src.common.models.job import JobRead
from src.scheduler.app.scheduler_conf import (
    jobstores,
    job_defaults)

class SchedulerApp(AppSvc):

    def __init__(self, settings: SchedulerAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.scheduler = BackgroundScheduler(jobstores=jobstores,
                                          job_defaults=job_defaults,
                                          timezone=utc)
    
    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    def _set_incoming_commands(self) -> dict:
        return {
            "task.create": self._create,
            "task.read": self._read,
            "task.read_all": self._read_all,
            "task.read_by_template": self._read_by_template,
            "task.read_by_schema": self._read_by_schema,
            "task.update": self._update,
            "task.delete": self._delete,
            "task.pause": self._pause,
            "task.resume": self._resume,
        }
    
    async def _create(self, mes) -> dict:
        cron, resource_url, schema_uuid, settings = mes.get('data').get('cron'),\
                                                    mes.get('data').get('resource_url'),\
                                                    mes.get('data').get('schema_uuid'),\
                                                    mes.get('data').get('settings')
        
        task_id = str(uuid4())
        resp = await self._post_message(mes={"action": "schema.read", "data": schema_uuid}, reply=True)
        schema, template_uuid = resp.get('schema'), resp.get('template_uuid')
        mes_data = mes.get('data')
        mes_data['item_collection_uuid'] = schema_uuid
        mes_data['schema'] = schema
        mes_data['template_uuid'] = template_uuid
        mes_data['task_uuid'] = task_id
        job = self.scheduler.add_job(
                                job_send_message,
                                CronTrigger.from_crontab(cron),
                                id=task_id,
                                kwargs={"amqp_url": self._config.amqp_url,
                                        "exchange_name": self._config.publish["main"]["name"],
                                        "body": {"action": "spider.start", "data": mes_data},
                                        "routing_key": "spider_app_consume"
                                        },
                                
                                )
        self._logger.info(f'Создано задание {job.id} для парсинга ресурса {resource_url} с расписанием {cron}')
        res = {
            "task_uuid": job.id,
            "resource_url": resource_url,
            "schema_uuid": schema_uuid,
            "template_uuid": template_uuid
        }
        return res


    async def _read(self, mes) -> dict:
        task_id = mes.get('task_id')
        job: Job = self.scheduler.get_job(job_id=task_id)
        if job:
            task_scheme = job.kwargs.get('body')
            return task_scheme
        else:
            res = {
                "id": task_id,
                "error": {
                    "message": "Задача с указанным task_id не найдена"
                }
            }
            return res
        
    async def _read_all(self, mes) -> dict:
        jobs: List[Job] = self.scheduler.get_jobs()
        res = []
        for job in jobs:
            job_obj = JobRead.model_validate(job.kwargs.get("body"))
            res.append({
                "id": job.id,
                "schema_uuid": job_obj.root.data.schema_uuid,
                "template_uuid": job_obj.root.data.template_uuid,
                "cron": job_obj.root.data.cron,
                "resource_url": job_obj.root.data.resource_url,
                "next_run": None if not job.next_run_time else job.next_run_time.isoformat(),
            })
        return res
    
    # async def _read_by_template(self, mes) -> dict:
    #     jobs: List[Job] = self.scheduler.get_jobs()
    #     res = []
    #     for job in jobs:
    #         job_obj = JobRead.model_validate(job.kwargs.get("body"))
    #         res.append({
    #             "id": job.id,
    #             "schema_uuid": job_obj.root.data.schema_uuid,
    #             "template_uuid": job_obj.root.data.template_uuid,
    #             "cron": job_obj.root.data.cron,
    #             "resource_url": job_obj.root.data.resource_url,
    #             "next_run": None if not job.next_run_time else job.next_run_time.isoformat(),
    #         })
    #     return res
    
    # async def _read_by_schema(self, mes) -> dict:
    #     jobs: List[Job] = self.scheduler.get_jobs()
    #     res = []
    #     for job in jobs:
    #         job_obj = JobRead.model_validate(job.kwargs.get("body"))
    #         res.append({
    #             "id": job.id,
    #             "schema_uuid": job_obj.root.data.schema_uuid,
    #             "template_uuid": job_obj.root.data.template_uuid,
    #             "cron": job_obj.root.data.cron,
    #             "resource_url": job_obj.root.data.resource_url,
    #             "next_run": None if not job.next_run_time else job.next_run_time.isoformat(),
    #         })
    #     return res

    async def _delete(self, mes) -> bool:
        task_id = mes.get('data')
        job: Job = self.scheduler.get_job(job_id=task_id)
        if job:
            job.remove()
            return True
        else:
            self._logger.error(f"Задача с указанным task_id {task_id} не найдена") 
            return False

    async def _update(self, mes) -> dict:
        task_id = mes.get('data')
        body = mes.get('body')
        job: Job = self.scheduler.get_job(job_id=task_id)
        if job:
            task_scheme = job.kwargs.get('body')
            task_kwargs = job.kwargs
            if body:
                app._logger.info(body)
                cron = body.get('cron')
                resource = body.get('resource')
                resource_name = resource.get('resource_name')
                resource_url = resource.get('resource_url')
                template = resource.get('template')
                task_scheme['cron'] = cron if cron else task_scheme['cron']
                task_scheme['resource']['resource_name'] = resource_name if resource_name else task_scheme['resource']['resource_name']
                task_scheme['resource']['resource_url'] = resource_url if resource_url else task_scheme['resource']['resource_url']
                task_scheme['resource']['template'] = template if template else task_scheme['resource']['template']
                task_kwargs['body'] = task_scheme
                job.modify(kwargs=task_kwargs)
                return task_scheme
            return task_scheme
        else:
            self._logger.error(f"Задача с указанным task_id {task_id} не найдена или не указан параметр обновления") 
            return False
            
    async def _pause(self, mes) -> bool:
        task_id = mes.get('data')
        job: Job = self.scheduler.get_job(job_id=task_id)
        if job:
            job.pause()
            return True
        else:
            self._logger.error(f"Задача с указанным task_id {task_id} не найдена") 
            return False
        
    async def _resume(self, mes) -> bool:
        task_id = mes.get('data')
        job: Job = self.scheduler.get_job(job_id=task_id)
        if job:
            job.resume()
            return True
        else:
            self._logger.error(f"Задача с указанным task_id {task_id} не найдена") 
            return False

    async def on_startup(self) -> None:
        await super().on_startup()
        self.scheduler.start()

    async def on_shutdown(self):
        await super().on_shutdown()
    
settings = SchedulerAppSettings()

app = SchedulerApp(settings=settings, title="`SchedulerApp` service")