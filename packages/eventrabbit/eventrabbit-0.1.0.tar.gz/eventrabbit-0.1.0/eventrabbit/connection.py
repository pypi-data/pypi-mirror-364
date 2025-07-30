import asyncio
from contextlib import suppress

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection

from .interface import IRabbitConnectionManager
from .logger import logger


class RabbitConnectionManager(IRabbitConnectionManager):
    """
    Manages RabbitMQ connection with idle timeout mechanism.
    This class provides a connection factory that automatically manages
    connection lifecycle, including creation, idle timeout, and cleanup.
    """

    def __init__(self, url: str, idle_timeout: int = 300):
        """
        Initialize the connection manager.
        Args:
            url: RabbitMQ connection URL
            idle_timeout: Time in seconds to wait before closing idle connection (default: 5 minutes)
        """
        self.url = url
        self.idle_timeout = idle_timeout
        self._connection: AbstractRobustConnection | None = None
        self._lock = asyncio.Lock()
        self._close_task: asyncio.Task | None = None
        self._idle_event = asyncio.Event()

    async def get_connection(self) -> AbstractRobustConnection:
        """
        Get or create a RabbitMQ connection.
        Returns:
            AbstractRobustConnection: The RabbitMQ connection
        Raises:
            Exception: If connection creation fails
        """
        async with self._lock:
            try:
                # Reset idle timer when connection is being used
                self._reset_idle_timer()

                if self._connection is None or self._connection.is_closed:
                    logger.info(f"Creating new RabbitMQ connection to {self.url}")
                    self._connection = await connect_robust(
                        url=self.url,
                        timeout=30,
                    )
                    logger.info("RabbitMQ connection established successfully")

                return self._connection
            except Exception as e:
                logger.error(f"Failed to create RabbitMQ connection: {e}")
                # Reset connection to None so next attempt creates a new one
                self._connection = None
                raise

    def _reset_idle_timer(self):
        """Reset the idle timer by setting and clearing the event"""
        self._idle_event.set()
        self._idle_event.clear()

    async def _schedule_close(self):
        """Schedule connection close after idle timeout"""
        try:
            # Wait for the idle timeout or until the event is set (connection used)
            await asyncio.wait_for(self._idle_event.wait(), timeout=self.idle_timeout)
        except asyncio.TimeoutError:
            # Timeout occurred, close the connection
            async with self._lock:
                if self._connection and not self._connection.is_closed:
                    logger.info(f"Closing idle RabbitMQ connection after {self.idle_timeout} seconds")
                    await self._connection.close()
                    self._connection = None
                self._close_task = None

    async def close_connection(self):
        """Close connection immediately"""
        async with self._lock:
            # Cancel any pending close task
            if self._close_task and not self._close_task.done():
                self._close_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self._close_task
                self._close_task = None

            if self._connection and not self._connection.is_closed:
                await self._connection.close()
                self._connection = None
                logger.info("RabbitMQ connection closed immediately")

    async def close_connection_with_timeout(self):
        """Close connection after idle timeout instead of immediately"""
        async with self._lock:
            # Cancel existing close task if any
            if self._close_task and not self._close_task.done():
                self._close_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self._close_task

            # Schedule new close task
            self._close_task = asyncio.create_task(self._schedule_close())
            logger.info(f"Scheduled connection close after {self.idle_timeout} seconds of inactivity")


def get_connection_rabbit(url: str, idle_timeout: int = 300):
    """
    Create connection factory with idle timeout mechanism.
    This function maintains backward compatibility by returning a tuple of functions
    that match the original interface.
    Args:
        url: RabbitMQ connection URL
        idle_timeout: Time in seconds to wait before closing idle connection (default: 5 minutes)
    Returns:
        tuple: (get_connection, close_connection, close_connection_with_timeout)
    """
    manager = RabbitConnectionManager(url, idle_timeout)
    return manager.get_connection, manager.close_connection, manager.close_connection_with_timeout
