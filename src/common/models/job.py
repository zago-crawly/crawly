from typing import Literal, Optional
from pydantic import BaseModel, Field, RootModel

from src.common.models.task import SpiderSettings

class JobBodyData(BaseModel):
  cron: str
  resource_url: str
  language: Optional[str] = None
  schema_uuid: str
  settings: Optional[SpiderSettings] = None
  item_collection_uuid: str
  schema: dict
  template_uuid: str
  task_uuid: str

class JobBody(BaseModel):
  action: Literal["spider.start"] = Field()
  data: JobBodyData

class JobBaseClass(RootModel):
  root: JobBody

class JobRead(JobBaseClass):
  pass