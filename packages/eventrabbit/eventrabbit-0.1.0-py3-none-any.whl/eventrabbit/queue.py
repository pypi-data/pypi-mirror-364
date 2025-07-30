from collections.abc import Awaitable
from typing import Callable
from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractRobustConnection
from .common import QueueData
from .interface import IRabbitQueue,ILogger


class RabbitQueue(IRabbitQueue):
    def __init__(
        self,
        exchange_name: str,
        logger: ILogger,
        get_connection: Callable[[], Awaitable[AbstractRobustConnection]],
        trace_id: int | None = None,
        on_publish_message: Callable | None = None,
        message_attributes: dict | None = None,
    ) -> None:
        super().__init__()
        self._exchange_name = exchange_name
        self._message_attributes = message_attributes or {}
        self._on_publish_message = on_publish_message
        self._logger = logger
        self._trace_id = trace_id
        self._get_connection = get_connection

    async def send(self, data: QueueData, routing_key: str = None) -> None:
        try:
            connection = await self._get_connection()
            async with connection.channel() as channel:
                exchange = await channel.get_exchange(
                    self._exchange_name,
                )

                message = Message(
                    body=data.model_dump_json().encode("utf-8"),
                    delivery_mode=DeliveryMode.PERSISTENT,
                )
                self._logger.info(
                    f"Send data to {self._exchange_name}:{routing_key}.data:{data.model_dump()}",
                    trace_id=self._trace_id,
                )
                return await exchange.publish(
                    message,
                    routing_key=routing_key if routing_key else "",
                )
        except Exception as e:
            self._logger.exception("Failed to send profile queue", exc=e)
            raise
