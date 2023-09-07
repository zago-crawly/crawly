import sys

sys.path.append(".")
from src.common.api_svc import APISettings


class SchedulerAPISettings(APISettings):
    
    svc_name: str = "scheduler_api"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    #: обменник для публикаций
    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "scheduler_api_publish"
        }
    }
    consume: dict = {
        "queue_name": "scheduler_api_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привзяка для очереди
                "routing_key": ["scheduler_api_consume"]
            }
        }
    }
