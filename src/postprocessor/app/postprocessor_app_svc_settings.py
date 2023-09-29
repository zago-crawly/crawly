import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class PostprocessorAppSettings(AppSettings):
    svc_name: str = "postprocessor_app"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    #: обменник для публикаций
    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "postprocessor_app_publish"
        }
    }
    consume: dict = {
        "queue_name": "postprocessor_app_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["postprocessor_app_consume", "postprocessor_api_publish"]
            }
        }
    }

