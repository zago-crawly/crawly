import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class SchemaStorageAppSettings(AppSettings):
    svc_name: str = "schema_storage_app"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    #: обменник для публикаций
    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "schema_storage_app_publish"
        }
    }
    consume: dict = {
        "queue_name": "schema_storage_app_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["schema_storage_app_consume", "schema_storage_api_publish", "scheduler_app_publish"]
            }
        }
    }
