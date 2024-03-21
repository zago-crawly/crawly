import sys
from typing import List
from uuid import uuid4
from pytz import utc
from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger


sys.path.append(".")
from src.common.app_svc import AppSvc
from src.scheduler.app.scheduler_job_send_message import job_send_message
from src.scheduler.app.scheduler_app_svc_settings import SchedulerAppSettings
from src.scheduler.app.crawly_sched.crawly_scheduler import CrawlyScheduler
from src.common.models.task import TaskUpdate
from src.common.models.job import JobRead
from src.scheduler.app.scheduler_conf import (
    jobstores,
    job_defaults)


class SchedulerApp(AppSvc):

    def __init__(self, settings: SchedulerAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.scheduler = CrawlyScheduler(jobstores=jobstores,
                                         job_defaults=job_defaults,
                                         timezone=utc)

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

    def _set_incoming_commands(self) -> dict:
        return {
            "task.create": self._create,
            "task.read": self._read,
            "task.read_all": self._read_all,
            "task.update": self._update,
            "task.delete": self._delete,
            "task.pause": self._pause,
            "task.resume": self._resume,
        }

    async def _create(self, mes) -> dict:
        cron, resource_url, schema_uuid, _ = mes.get('data').get('cron'), \
                                             mes.get('data').get('resource_url'), \
                                             mes.get('data').get('schema_uuid'), \
                                             mes.get('data').get('settings')

        task_uuid = str(uuid4())  # TODO Make so that crawly_jobstore generated uuid itselft and returns it
        resp = await self._post_message(mes={"action": "schema.read", "data": schema_uuid}, reply=True)
        if resp.get('error'):
            return resp
        schema, template_uuid = resp.get('schema'), resp.get('template_uuid')
        mes_data = mes.get('data')
        mes_data['item_collection_uuid'] = schema_uuid
        mes_data['schema'] = schema
        mes_data['template_uuid'] = template_uuid
        mes_data['task_uuid'] = task_uuid
        job = self.scheduler.add_job(
                                job_send_message,
                                template_uuid=template_uuid,
                                schema_uuid=schema_uuid,
                                trigger=CronTrigger.from_crontab(cron),
                                id=task_uuid,
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
        task_uuid = mes.get('task_uuid')
        job: Job = self.scheduler.get_job(job_id=task_uuid)
        if job:
            task_scheme = job.kwargs.get('body')
            return task_scheme
        else:
            res = {
                "id": task_uuid,
                "error": {
                    "message": "Задача с указанным task_uuid не найдена"
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
                # "status":                
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
        task_uuid = mes.get('data')
        job: Job = self.scheduler.get_job(job_id=task_uuid)
        if job:
            job.remove()
            return True
        else:
            self._logger.error(f"Задача с указанным task_uuid {task_uuid} не найдена")
            return False

    async def _update(self, mes) -> dict:
        partial_task: TaskUpdate = TaskUpdate.model_validate(mes.get('data'))
        job: Job = self.scheduler.get_job(job_id=partial_task.task_uuid)
        if job:
            job_kwargs = job.kwargs
            old_task = TaskUpdate.model_validate(job.kwargs['body']['data'])
            updated_task = old_task.model_copy(update=partial_task.model_dump(exclude_none=True), deep=True)
            job_kwargs['body']['data']['resource_url'] = updated_task.resource_url
            job_kwargs['body']['data']['cron'] = updated_task.cron
            job_kwargs['body']['data']['language'] = updated_task.language
            job.modify(kwargs=job_kwargs)
            return job_kwargs.get('body').get('data')
        else:
            self._logger.error(f"Задача c указанным task_uuid {partial_task.task_uuid} не найдена или не указан параметр обновления")
            return False

    async def _pause(self, mes) -> bool:
        task_uuid = mes.get('data')
        job: Job = self.scheduler.get_job(job_id=task_uuid)
        if job:
            job.pause()
            return True
        else:
            self._logger.error(f"Задача с указанным task_uuid {task_uuid} не найдена")
            return False

    async def _resume(self, mes) -> bool:
        task_uuid = mes.get('data')
        job: Job = self.scheduler.get_job(job_id=task_uuid)
        if job:
            job.resume()
            return True
        else:
            self._logger.error(f"Задача с указанным task_uuid {task_uuid} не найдена")
            return False

    async def on_startup(self) -> None:
        await super().on_startup()
        self.scheduler.start()

    async def on_shutdown(self):
        await super().on_shutdown()


settings = SchedulerAppSettings()

app = SchedulerApp(settings=settings, title="`SchedulerApp` service")
