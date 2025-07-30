
import asyncio
import json

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel

from .common import ConsumeChannel, QueueConfig, RetryConfig
from .context import ContextConnectionEvents
from .exceptions import ActionNotFoundError, HandlerNotFoundError, MessageDataNotFoundError
from .interface import IEventHandler
from .model import QueueDetail, QueueResponse


class EventHandler(IEventHandler):
    def __init__(
            self,
            context_event: ContextConnectionEvents,
            logger,
            retry_config: RetryConfig = None,
            queue_config: QueueConfig = None,
    ):
        self._context_event = context_event
        self._logger = logger
        self._retry_config = retry_config if retry_config else RetryConfig()
        self._queue_config = queue_config if queue_config else QueueConfig()

    async def init_queue_and_exchange(
            self,
            url: str,
            queue_name: str,
            exchange_name: str | None,
            exchange_type: aio_pika.ExchangeType,
    ):
        """
        Connects to RabbitMQ, initializes the channel, queue, and exchange (if needed).
        Returns connection, channel, queue.
        :param url: Connection URL
        :param queue_name: Queue name
        :param exchange_name: Exchange name
        :param exchange_type: Exchange type
        :return: connection, channel, queue
        """
        connection = await aio_pika.connect_robust(url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=self._queue_config.prefetch_count)
        queue = await channel.declare_queue(
            queue_name,
            durable=self._queue_config.durable,
        )
        if exchange_name is not None:
            exchange = await channel.declare_exchange(exchange_name, exchange_type)
            await queue.bind(exchange)
        return connection, channel, queue

    async def consume(self, channel: ConsumeChannel) -> None:
        """
        Main loop: connects to RabbitMQ, listens to the queue, processes messages, retries on errors.
        :param channel: ConsumeChannel object containing connection parameters
        """

        while True:
            try:
                self._logger.info(
                    f"Connecting to RabbitMQ for queue: {channel.queue_name} (Exchange: {channel.exchange_name})...",
                )
                connection, amqp_channel, queue = await self.init_queue_and_exchange(
                    channel.url,
                    channel.queue_name,
                    channel.exchange_name,
                    channel.exchange_type,
                )
                async with connection:
                    self._logger.info(
                        f"Listening on queue: {channel.queue_name} (Exchange: {channel.exchange_name})",
                    )
                    async with queue.iterator() as queue_iter:
                        async for message in queue_iter:
                            await self.handle_single_message(
                                message,
                                channel.queue_name,
                                amqp_channel,
                                channel.exchange_name,
                            )
            except (aio_pika.exceptions.AMQPConnectionError, aio_pika.exceptions.AMQPChannelError) as e:
                self._logger.error(
                    f"[{channel.queue_name}] RabbitMQ connection error: {e}. Retrying in 5 seconds...",
                )
                await asyncio.sleep(5)

    async def process_message(self, message: dict) -> tuple[QueueDetail, object]:
        """
        Processes the message dictionary: determines the action, finds the handler, calls it, and returns queue_detail and the result.
        :param message: Dictionary with message data
        :return: (queue_detail, handler result)
        :raises ActionNotFoundError, HandlerNotFoundError, MessageDataNotFoundError
        """
        action = message.get("action")
        if action is None:
            err_msg = f"Action not found; Raw message: {message}"
            raise ActionNotFoundError(err_msg)

        handler_data = self._context_event.get_connect(action)
        if handler_data is None:
            err_msg = f'Handler for action "{action}" not found; Raw message: {message}'
            raise HandlerNotFoundError(err_msg)

        queue_detail, handler = handler_data
        message_data = message.get("data")
        if message_data is None:
            err_msg = f"Message data not found; Raw message: {message}"
            raise MessageDataNotFoundError(err_msg)

        result = await handler(**message_data)
        self._logger.debug(
            f"Task execution for user {message_data.get('user_id',None)} " +
            f"Message: {message_data}. " +
            f"The action is: {action}. " +
            f"The result is: {result}",
        )
        return queue_detail, result

    @staticmethod
    async def handle_reply_data(channel: AbstractRobustChannel, data, reply_to: str, correlation_id: str):
        """
        Sends a reply message (RPC) to the specified reply_to with correlation_id.
        :param channel: RabbitMQ channel
        :param data: Data to send
        :param reply_to: Reply queue
        :param correlation_id: Correlation identifier
        """
        data = QueueResponse(
            data=data,
        )
        reply_message = Message(
            body=data.model_dump_json().encode("utf-8"),
            correlation_id=correlation_id,
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await channel.default_exchange.publish(
            reply_message,
            routing_key=reply_to,
        )

    @staticmethod
    def _get_retry_count_from_headers(message) -> int:
        """
        Gets retry count from message headers
        :param message: RabbitMQ message
        :return: Current retry count
        """
        headers = message.headers or {}
        return headers.get("x-retry-count", 0)

    @staticmethod
    def _should_retry_message(retry_count: int, max_retries: int) -> bool:
        """
        Determines if message should be retried based on retry count and max retries
        :param retry_count: Current retry count
        :param max_retries: Maximum allowed retries (-1 for infinite)
        :return: True if should retry, False otherwise
        """
        if max_retries == -1:  # Infinite retries
            return True
        return retry_count < max_retries

    async def _handle_message_retry(self, message: AbstractIncomingMessage, channel, exchange_name=None):
        """
        Handles message retry logic with delay
        :param message: RabbitMQ message
        :param channel: RabbitMQ channel for republishing
        :param exchange_name: Exchange name to republish to
        """
        current_retry_count = self._get_retry_count_from_headers(message)

        if self._should_retry_message(current_retry_count, self._retry_config.max_retries):
            # Increment retry count
            new_retry_count = current_retry_count + 1

            # Update message headers with new retry count
            headers = message.headers or {}
            headers["x-retry-count"] = new_retry_count

            self._logger.warning(
                f"Message processing failed. Retry {new_retry_count} of "
                f"{'∞' if self._retry_config.max_retries == -1 else self._retry_config.max_retries}. "
                f"Message will be retried in {self._retry_config.retry_delay_seconds} seconds via TTL.",
            )

            # Create new message with updated headers and delay
            retry_message = Message(
                body=message.body,
                headers=headers,
                delivery_mode=message.delivery_mode,
                priority=message.priority,
                correlation_id=message.correlation_id,
                reply_to=message.reply_to,
                message_id=message.message_id,
                timestamp=message.timestamp,
                type=message.type,
                user_id=message.user_id,
                app_id=message.app_id,
            )

            # Publish the retry message to the same exchange and routing key
            if exchange_name:
                # Get the specific exchange
                exchange = await channel.get_exchange(exchange_name)
                await exchange.publish(
                    retry_message,
                    routing_key=message.routing_key or "",
                )
            else:
                # Fallback to default exchange if no specific exchange provided
                await channel.default_exchange.publish(
                    retry_message,
                    routing_key=message.routing_key or "",
                )

            # Acknowledge the original message to remove it from queue
            await message.ack()
        else:
            self._logger.error(
                f"Message processing failed after {current_retry_count} retries. "
                f"Max retries ({self._retry_config.max_retries}) exceeded. Message rejected permanently.",
            )
            # Reject without requeue to move to dead letter queue or discard
            await message.reject(requeue=False)

    async def handle_single_message(self, message: AbstractIncomingMessage, queue_name, channel, exchange_name=None):
        """
        Processes a single message from the queue:parses, calls the handler, publishes the result or sends an RPC reply.
        :param message: Message from the queue
        :param queue_name: Queue name
        :param channel: RabbitMQ channel
        :param exchange_name: Exchange name for retry
        """
        try:
            raw_message = message.body
            message_as_dict = json.loads(raw_message)
            (queue_detail, result_message) = await self.process_message(message_as_dict)
            self._logger.info(
                f"[{queue_name}] Processed message: {result_message}",
            )

            if message.reply_to:
                await self.handle_reply_data(
                    channel,
                    result_message,
                    message.reply_to,
                    message.correlation_id,
                )
            await message.ack()

        except Exception as e:  # noqa
            self._logger.error(
                f"[{queue_name}] Exception: {e}; Raw message: {getattr(message, 'body', None)};",
            )
            await self._handle_message_retry(message, channel, exchange_name)
