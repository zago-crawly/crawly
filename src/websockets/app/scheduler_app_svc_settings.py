import sys

sys.path.append(".")
from src.common.base_svc_settings import SvcSettings


class SchedulerAppSettings(SvcSettings):
    svc_name: str = "scheduler_app"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"
    #: Версия API
    api_version: str = "v1"

    #: обменник для публикаций
    publish: dict = {
        "main": {
            "name": "scheduler_app",
            "type": "direct",
            "routing_key": "scheduler_app"
        }
    }
    consume: dict = {
        "main": {
            "name": "scheduler_api",
            "type": "direct",
            "queue_name": "scheduler_api",
            "routing_key": "scheduler_api"
        }
    }

