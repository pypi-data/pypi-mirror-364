from abc import ABC, abstractmethod
from typing import Callable

from aio_pika.abc import AbstractRobustConnection

from .common import ConsumeChannel, QueueData
from .model import QueueDetail

class ILogger(ABC):
    @abstractmethod
    def info(self, message: str, trace_id: str | None = None):
        pass

    @abstractmethod
    def warning(self, message: str, trace_id: str | None = None):
        pass

    @abstractmethod
    def error(self, message: str, trace_id: str | None = None):
        pass

    @abstractmethod
    def debug(self, message: str, trace_id: str | None = None):
        pass

    @abstractmethod
    def exception(self, message: str, exc: Exception | None, **kwargs):
        pass

class IRabbitQueue(ABC):
    @abstractmethod
    async def send(self, data: QueueData,routing_key:str=None):
        raise NotImplementedError


class IEventDecorators(ABC):
    @abstractmethod
    def consumer(
            self,
            action: str,
    ):
       pass

    @abstractmethod
    def producer(
            self,
            exchange_name: str,
            action: str,
            key: str = None,
    ):
        pass

    @abstractmethod
    def function(
            self,
            action: str,
            exchange_name: str,
            action_reply: str = None,
            key: str = None,
    ):
        pass

class IEventHandler(ABC):
    @abstractmethod
    async def consume(self,channel:ConsumeChannel):
        pass

class IContextConnectionEvent(ABC):
    @abstractmethod
    def connect(
            self,
            action:str,
            queue_detail:QueueDetail,
            func:Callable,
    ):
        pass

    @abstractmethod
    def get_connect(self,action: str) -> tuple[QueueDetail,Callable] | None:
        pass


class IRabbitConnectionManager(ABC):
    """
    Manages RabbitMQ connection with idle timeout mechanism.
    This class provides a connection factory that automatically manages
    connection lifecycle, including creation, idle timeout, and cleanup.
    """
    @abstractmethod
    async def get_connection(self) -> AbstractRobustConnection:
        pass

    @abstractmethod
    async def close_connection(self):
        pass

    @abstractmethod
    async def close_connection_with_timeout(self):
        pass
