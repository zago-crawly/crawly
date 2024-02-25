from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import Optional
import sys

sys.path.append(".")

class TaskBaseClass(BaseModel):
    cron: str = Field(title="", description="")
    resource_url: str = Field(title="", description="")
    language: Optional[str] = None
    schema_uuid: str = Field(title="UUID схемы для парсинга") 


class SpiderSettings(BaseSettings):
    # Параметр размера очереди, которая используется при парсинге ресурса
    # Размер имеет значение при частоте обновления ресурса. Если ресурс постоянно обновляется
    # то при маленьком размере очереди некоторые новые данные не смогут попасть в очередь из за ограничения размера.
    max_items: Optional[int] = Field(default=10,
                               ge=1,
                               le=100, 
                               description="""Параметр максимального количества элементов, которая используется при парсинге ресурса
                               Размер имеет значение при частоте обновления ресурса. Если ресурс постоянно обновляется
                               то при маленьком количестве некоторые новые данные 
                               не смогут попасть в очередь из за ограничения размера.""")
    

class TaskCreate(TaskBaseClass):
    """
    Базовый класс для команды создания задания.
    Наследуется от модели класса ResourceCreate, но добавляется поле cron –
    расписание, по которому будет работать календарь задач
    """
    settings: Optional[SpiderSettings] = None


class TaskCreateResult(BaseModel):
    """Модель которая возвращается при создании нового задания в календаре
    Наследуется от модели ResourceCreateResult, новых поле не добавляется
    """
    task_uuid: str = Field(title="", description="")
    resource_url: str = Field(title="", description="")
    schema_uuid: str = Field(title="", description="")

class TaskRead(TaskBaseClass):
    pass

class TaskDelete(BaseModel):
    task_id: str = Field(title="", description="")

class TaskUpdate(BaseModel):
    task_uuid: str = Field()
    cron: Optional[str] = Field(title="", description="")
    resource_url: Optional[str] = Field(title="", description="")
    language: Optional[str]
    schema_uuid: Optional[str] = Field(title="UUID схемы для парсинга")

class TaskUpdateResult(TaskRead):
    pass

class TaskForSpider(TaskCreate):
    task_uuid: str = Field(title="", description="")
    template_uuid: str = Field(title="UUID шаблона схемы парсинга")
    schema_for_spider: dict = Field(alias='schema')
    