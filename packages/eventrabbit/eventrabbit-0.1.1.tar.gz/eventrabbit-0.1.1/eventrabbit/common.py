from dataclasses import dataclass
from typing import Any

import aio_pika
from pydantic import BaseModel


class RetryConfig(BaseModel):
    """Configuration for message retry settings"""
    max_retries: int = -1  # -1 means infinite retries
    retry_delay_seconds: int = 5  # Delay between retries in seconds


@dataclass
class QueueConfig:
    """Configuration for queue settings"""
    prefetch_count: int = 10  # Number of messages to prefetch
    durable: bool = True


class QueueData(BaseModel):
    action: str
    data: dict

class QueueResponse(BaseModel):
    data: Any

@dataclass
class ConsumeChannel:
    url: str
    queue_name: str
    exchange_type: aio_pika.ExchangeType
    exchange_name: str | None = None
    queue_config: QueueConfig | None = None
