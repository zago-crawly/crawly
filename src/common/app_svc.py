"""
Модуль содержит базовый класс ``Svc`` - предок всех сервисов.
"""
import sys
from typing import Optional
import json
import operator
from functools import reduce

sys.path.append(".")

from src.common.app_svc_settings import AppSettings
from src.common.base_svc import BaseSvc


class AppSvc(BaseSvc):
    """
    Класс ``Svc`` - наследник класса :class:`BaseSvc`

    Реализует дополнительную функциональность:

    * коннект к иерархии;
    * логика подписок на сообщения между сервисами.

    Args:
            settings (Settings): конфигурация приложения см. :class:`~svc_settings.SvcSettings`
    """

    def __init__(self, settings: AppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self._amqp_subscribe = {}

    def _set_incoming_commands(self) -> dict:
        # словарь входящих команд переопределяем в каждом классе-наследнике,
        # так как CRUD-команды в каждой группе сервисов начинаются с
        # с имени "своей" сущности
        # если сервис зависит от нескольких сущностей, как, к примеру,
        # методы могут быть привязаны к тегам, тревогам, расписаниям,
        # то в _incoming_messages может быть несколько ключей
        # ...mayUpdate, ...updating и т.д.

        return {
            "create": self._create,
            "read": self._read,
            "update": self._update,
            "delete": self._delete,
            "mayUpdate": self._may_update,
            "updating": self._updating,
            "mayDelete": self._may_delete,
            "deleting": self._deleting
        }

    def set_signals(before: Optional[str] = None,
                    after: Optional[str] = None,
                    data: Optional[dict | str] = {},
                    path_to_obj_id: Optional[str] = "data"):
        def inner(fn):
            async def wrap(self, mes):
                obj_id = ""
                if path_to_obj_id:
                    obj_id = reduce(operator.getitem, path_to_obj_id.split('.'), mes)
                await self._post_message(mes=json.dumps({"signal": before, "data": {"id": obj_id, "data": data}}))
                res = await fn(self, mes)
                await self._post_message(mes=json.dumps({"signal": after, "data": {"id": obj_id, "data": res if res else data}}))
                return res
            return wrap
        return inner

    async def _amqp_connect(self) -> None:
        await super()._amqp_connect()

        # создадим подписки
        for key, item in self._config.subscribe.items():
            self._amqp_subscribe[key] = {
                "publish": {},
                "consume": {}
            }

            # сюда будем публиковать заявки на уведомления
            self._amqp_subscribe[key]["publish"]["exchange"] = \
                await self._amqp_channel.declare_exchange(
                    item["publish"]["name"], item["publish"]["type"], durable=True
            )
            self._amqp_subscribe[key]["publish"]["routing_key"] = \
                item["publish"]["routing_key"]

            # для получения уведомлений подсоединим свою главную очередь
            self._amqp_subscribe[key]["consume"]["exchange"] = \
                await self._amqp_channel.declare_exchange(
                    item["consume"]["name"], item["consume"]["type"], durable=True
            )
            await self._amqp_consume["queue"].bind(
                exchange=self._amqp_subscribe[key]["consume"]["exchange"],
                routing_key=self._amqp_subscribe[key]["consume"]["routing_key"]
            )

    async def _create(self, mes: dict) -> dict:
        ...
        
    async def _read(self, mes: dict) -> dict:
        ...
        
    async def _delete(self, mes: dict) -> dict:
        ...
        
    async def _update(self, mes: dict) -> dict:
        ...

    async def on_startup(self) -> None:
        await super().on_startup()
