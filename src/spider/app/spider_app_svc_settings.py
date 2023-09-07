import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class SpiderAppSettings(AppSettings):
    svc_name: str = "spider_app"
    
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    #: обменник для публикаций
    publish: dict[str, dict] = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "spider_app_publish"
        }
    }
    
    consume: dict = {
        "queue_name": "spider_app_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["spider_app_consume", "sheduler_app_publish"]
            }
        }
    }

