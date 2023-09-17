import sys

sys.path.append(".")
from src.common.app_svc_settings import AppSettings


class SignalAppSettings(AppSettings):
    
    svc_name: str = "signal_app"
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://crwl:Crawly97@rabbitmq/"

    publish: dict = {
        "main": {
            "name": "crawly",
            "type": "direct",
            "routing_key": "signal_app_publish"
        }
    }
    consume: dict = {
        "queue_name": "signal_app_consume",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "crawly",
                #: тип обменника
                "type": "direct",
                #: привязка для очереди
                "routing_key": ["signal_app_consume",
                                "signal_api_publish",
                                "signal_app_api_publish"]
            }
        }
    }

