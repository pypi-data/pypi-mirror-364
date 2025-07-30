from enum import Enum
from typing import Any

from pydantic import BaseModel


class QueueType(str, Enum):
    QUEUE = "queue"

class QueueEventType(str, Enum):
    CONSUME = "consume"


class QueueDetail(BaseModel):
    action: str
    key: str | None = None
    exchange_name: str | None = None
    queue_type: QueueEventType

class QueueResponse(BaseModel):
    data: Any
