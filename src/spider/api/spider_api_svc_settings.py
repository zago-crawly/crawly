import sys

sys.path.append(".")
from src.common.api_svc_settings import APISettings


class SpiderAPISettings(APISettings):
    svc_name: str = "spider_api"
    
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    #: обменник для публикаций
    publish: dict[str, dict] = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "spider_api_publish"
        }
    }
    
    consume: dict = {
        "queue_name": "spider_api_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["spider_api_consume", "sheduler_app_publish"]
            }
        }
    }

