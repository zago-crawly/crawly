"""
Класс, от которого наследуются все классы-настройки для сервисов.
Наследуется от класса ``pydantic.BaseSettings``, все настройки передаются
в json-файлах либо в переменных окружения.
По умолчанию имя файла с настройками - ``config.json``.
Имя конфигурационного файла передаётся сервису в переменной окружения
``config_file``.
"""

import sys

sys.path.append(".")

from src.common.base_svc_settings import BaseSvcSettings

class AppSettings(BaseSvcSettings):

    subscribe: dict = {
         # сущность, уведомления об изменение/удаление узлов которой
         # требуются сервису
         # "<сущность_2>": {
            # в этот обменник сервис будет посылать сообщение "subscribe"
         #  "publish": {
         #      "name": "<сущность_2>",
         #      "type": "direct",
         #      "routing_key": "<сущность_2>_model_crud_consume"
         #   },
            # обменник, из которого сервис будет получать уведомления об
            # изменениях узлов
            # (к этому обменнику, с указанным routing_key будет привязана
            # главная очередь сервиса с управляющими командами)
         #   "consume": {
         #      "name": "<сущность_2>",
         #      "type": "direct",
         #      "routing_key": "<сущность_2>_model_crud_publish"
         #   }
         # }

      }
