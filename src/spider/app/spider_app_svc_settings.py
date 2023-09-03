import sys

sys.path.append(".")
from src.common.base_svc_settings import BaseSettings


class SpiderAppSettings(BaseSettings):
    svc_name: str = "spider_app"    

    #: обменник для публикаций
    publish: dict = {
        "name": "spider_app",
        "type": "direct",
        "routing_key": "spider_app"
    }

