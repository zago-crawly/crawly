import json
import sys

sys.path.append(".")

from src.common.models.task import TaskForSpider

def get_resource(item_file_path: str):
    with open(item_file_path) as f:
        dict_item = json.JSONDecoder().decode(f.read())
        parsed_item = TaskForSpider.parse_obj(dict_item)
        return parsed_item