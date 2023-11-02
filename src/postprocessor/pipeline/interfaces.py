from fastcore.transform import Transform
from typing import Any


class BaseProcessor(Transform):
    """ Interface for response processor

    Args:
        Transform (_type_): _description_
    """
    def encodes(self, data: Any) -> Any:
        ...