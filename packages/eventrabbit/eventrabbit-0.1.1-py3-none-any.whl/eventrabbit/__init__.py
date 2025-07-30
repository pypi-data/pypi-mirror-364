from .common import QueueConfig, RetryConfig
from .connection import RabbitConnectionManager
from .decorators import EventDecorators
from .context import ContextConnectionEvents
from .logger import logger
from .queue_runtime import EventHandler


def build_event_dependencies(
        url:str,
        idle_timeout:int = 300,
        retry_config:RetryConfig = None,
        queue_config:QueueConfig = None,
):
    context_event = ContextConnectionEvents()
    event_decorators = EventDecorators(
        url=url,
        idle_timeout=idle_timeout,
        context_connection=context_event,
        connection_rabbit=RabbitConnectionManager(
            url=url,
            idle_timeout=idle_timeout,
        ),
    )
    event_handle = EventHandler(
        context_event=context_event,
        logger=logger,
        retry_config=retry_config,
        queue_config=queue_config,
    )

    return event_decorators, event_handle
