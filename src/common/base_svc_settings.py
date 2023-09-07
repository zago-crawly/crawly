"""
Класс, от которого наследуются все классы-настройки для сервисов.
Наследуется от класса ``pydantic.BaseSettings``, все настройки передаются
в json-файлах либо в переменных окружения.
По умолчанию имя файла с настройками - ``config.json``.
Имя конфигурационного файла передаётся сервису в переменной окружения
``config_file``.
"""

import os

import json
from pathlib import Path
from typing import Any
from pydantic_settings import BaseSettings

def json_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    try:
        return json.loads(Path(os.getenv('config_file', 'config.json')).read_text(encoding))
    except Exception:
        return {}

class BaseSvcSettings(BaseSettings):
    #: имя сервиса
    svc_name: str = ""
    #: строка коннекта к RabbitMQ
    amqp_url: str = "amqp://prs:Peresvet21@rabbitmq/"

    # описание обменников, в которые сервис будет публиковать свои сообщения
    # наиболее часто это всего один обменник, описанный в ключе "main"
    # информацию об обменниках и сообщениях см. в документации на каждый
    # конкретный сервис
    publish: dict = {
        #: главный обменник
        # "main": {
            #: имя обменника
        #   "name": "base_svc",
            #: тип обменника
        #    "type": "direct",
            #: routing_key, с которым будут публиковаться сообщения обменником
            #: pub_exchange_type
        #    "routing_key": ["base_svc_publish"]
        #}
    }

    # описание обменников, из которых сервис получает сообщения
    # информацию об обменниках и сообщениях см. в документации на каждый
    # конкретный сервис
    # все сообщения для сервиса попадают в одну очередь (за исключением
    # ответов по RPC)
    consume: dict = {
        '''
        "queue_name": "base_svc",
        "exchanges": {
            "main": {
                #: имя обменника
                "name": "base_svc",
                #: тип обменника
                "type": "direct",
                #: имя очереди, из которой сервис будет получать сообщения
                "queue_name": "base_svc_consume",
                #: привзяка для очереди
                "routing_key": ["base_svc_consume"]
            }
        }
        '''
    }

    log: dict = {
        "level": "CRITICAL",
        "file_name": "peresvet.log",
        "retention": "1 months",
        "rotation": "20 days"
    }

    class Config:
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                env_settings,
                init_settings,
                json_config_settings_source,
                file_secret_settings,
            )
