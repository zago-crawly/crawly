import sys

sys.path.append(".")
from src.common.base_svc_settings import SvcSettings


class SchedulerAPISettings(SvcSettings):
    svc_name: str = "scheduler_api"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"
    #: Версия API
    api_version: str = "/v1"

    #: обменник для публикаций
    publish: dict[str, dict] = {
        "main": {
            "name": "scheduler_api",
            "type": "direct",
            "routing_key": "scheduler_api"
        }
    }
    consume: dict[str, dict] = {
        "main": {
            "name": "scheduler_api",
            "type": "direct",
            "queue_name": "scheduler_api",
            "routing_key": "scheduler_api"
        }
    }

