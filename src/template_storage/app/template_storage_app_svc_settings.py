import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class TemplateStorageAppSettings(AppSettings):
    
    svc_name: str = "template_storate_app"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "template_storage_app_publish"
        }
    }
    consume: dict = {
        "queue_name": "template_storage_app_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["template_storage_app_consume", "template_storage_api_publish", "schema_storage_app_publish"]
            }
        }
    }

