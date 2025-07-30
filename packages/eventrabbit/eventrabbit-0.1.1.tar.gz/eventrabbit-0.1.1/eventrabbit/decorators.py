from contextlib import suppress
from functools import wraps

from .common import QueueData
from .interface import IContextConnectionEvent, IEventDecorators, IRabbitConnectionManager
from .logger import logger
from .model import QueueDetail, QueueEventType
from .queue import RabbitQueue


class EventDecorators(IEventDecorators):
    def __init__(
            self,
            context_connection: IContextConnectionEvent,
            connection_rabbit: IRabbitConnectionManager,
            url: str,
            idle_timeout: int = 300,
    ):
        self.url = url
        self.idle_timeout = idle_timeout
        self._connection_rabbit_manager = connection_rabbit
        self._context_connection = context_connection

    def consumer(self, action: str):
        """Decorator for consumer"""
        def decorator(func):
            self._context_connection.connect(
                action=action,
                queue_detail=QueueDetail(
                    action=action,
                    queue_type=QueueEventType.CONSUME,
                ),
                func=func,
            )
            return func
        return decorator

    def producer(self, exchange_name: str, action: str, key: str = None):
        """Decorator for producer"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    data = await func(*args, **kwargs)
                    queue = RabbitQueue(
                        exchange_name=exchange_name,
                        logger=logger,
                        get_connection=self._connection_rabbit_manager.get_connection,
                    )
                    await queue.send(
                        data=QueueData(
                            data=data,
                            action=action,
                        ),
                        routing_key=key,
                    )
                    return data
                except Exception as e:
                    logger.error(f"Error in function decorator: {e}")
                    # Try to close connection on error
                    with suppress(Exception):
                        await self._connection_rabbit_manager.close_connection()
                    raise
                finally:
                    # Schedule connection close with timeout instead of immediate close
                    with suppress(Exception):
                        await self._connection_rabbit_manager.close_connection_with_timeout()
            return wrapper
        return decorator

    def function(self, action: str, exchange_name: str, action_reply: str = None, key: str = None):
        """Decorator for function with message sending"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    data = await func(*args, **kwargs)
                    queue = RabbitQueue(
                        exchange_name=exchange_name,
                        logger=logger,
                        get_connection=self._connection_rabbit_manager.get_connection,
                    )
                    await queue.send(
                        data=QueueData(
                            data=data,
                            action=action_reply or action,
                        ),
                        routing_key=key,
                    )
                    return data
                except Exception as e:
                    logger.error(f"Error in function decorator: {e}")
                    # Try to close connection on error
                    with suppress(Exception):
                        await self._connection_rabbit_manager.close_connection()
                    raise
                finally:
                    # Schedule connection close with timeout instead of immediate close
                    with suppress(Exception):
                        await self._connection_rabbit_manager.close_connection_with_timeout()

            self._context_connection.connect(
                action=action,
                queue_detail=QueueDetail(
                    action=action_reply or action,
                    queue_type=QueueEventType.CONSUME,
                ),
                func=wrapper,
            )

            return wrapper
        return decorator
