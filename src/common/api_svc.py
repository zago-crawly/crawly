import sys
from pydantic import BaseModel

sys.path.append(".")
from src.common.base_svc import BaseSvc
from src.common.api_svc_settings import APISettings


class APISvc(BaseSvc):

    # так как сообщения, создаваемые сервисами каждой сущности
    # начинаются с имени этой сущности, то
    # каждый сервис-наследник класса APICRUDSvc должен
    # определить "свои" CRUD-сообщения в этом словаре
    # к примеру, для сервиса TagsAPICRUDSvc:
    # {
    #   "create": "tags.create",
    #   "read": "tags.read",
    #   "update": "tags.update",
    #   "delete": "tags.delete"
    # }
    _outgoing_commands = {
        "create": "create",
        "read": "read",
        "update": "update",
        "delete": "delete"
    }

    def __init__(self, settings: APISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.api_version = settings.api_version

    async def create(self, payload: dict) -> dict:
        body = {
            "action": self._outgoing_commands["create"],
            "data": payload
        }

        return await self._post_message(mes=body, reply=True)

    async def update(self, payload: dict | str) -> dict:
        body = {
            "action": self._outgoing_commands["update"],
            "data": payload
        }

        return await self._post_message(mes=body, reply=True)

    async def read(self, payload: dict | str) -> dict:
        body = {
            "action": self._outgoing_commands["read"],
            "data": payload
        }

        return await self._post_message(mes=body, reply=True)

    async def delete(self, payload: dict | str) -> dict:
        body = {
            "action": self._outgoing_commands["delete"],
            "data": payload
        }

        return await self._post_message(mes=body, reply=True)
