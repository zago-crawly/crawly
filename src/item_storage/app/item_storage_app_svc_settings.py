import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class ItemStorageAppSettings(AppSettings):
    svc_name: str = "item_storage_app"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"
    
    #: обменник для публикаций
    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "item_storage_app_publish"
        }
    }
    consume: dict = {
        "queue_name": "item_storage_app_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["item_storage_app_consume", "item_storage_api_publish"]
            }
        }
    }

