import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class SignalAppAPISettings(AppSettings):
    
    svc_name: str = "signal_app_api"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "signal_app_api_publish"
        }
    }
    consume: dict = {
        "queue_name": "signal_app_api_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["signal_app_api_consume",
                                # Template Storage Services
                                "template_storage_api_publish",
                                "template_storage_app_publish",
                                # Schema Storage Services
                                "schema_storage_api_publish",
                                "schema_storage_app_publish",
                                # Scheduler Services
                                "scheduler_api_publish",
                                "scheduler_app_publish",
                                # Spider Services
                                "spider_app_publish",
                                # Item Storage Services
                                "item_storage_api_publish",
                                "item_storage_app_publish",
                                ]
            }
        }
    }

