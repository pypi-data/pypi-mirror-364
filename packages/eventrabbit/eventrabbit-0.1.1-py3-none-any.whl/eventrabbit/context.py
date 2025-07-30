from typing import Callable

from .interface import IContextConnectionEvent
from .model import QueueDetail


class ContextConnectionEvents(IContextConnectionEvent):
    _store_context:dict[str,(QueueDetail,Callable)]
    def __init__(self):
        self._store_context = {}

    def connect(self, action: str, queue_detail: QueueDetail, func: Callable):
        self._store_context[action] = (queue_detail,func)

    def get_connect(self, action: str) -> tuple[QueueDetail, Callable] | None:
        return self._store_context.get(action,None)
