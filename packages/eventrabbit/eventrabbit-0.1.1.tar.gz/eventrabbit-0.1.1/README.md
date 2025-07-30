# eventrabbit

A library for asynchronous work with RabbitMQ, implementing the **Event Sourcing** pattern. It allows you to easily build an event-driven architecture using decorators for producers, consumers, and functions.

## Purpose

Implements the **event sourcing** pattern: all state changes in the system are represented as events, which are sent and processed via the RabbitMQ message queue.

## Message Structure

All messages processed by the library must have the following format:

```json
{
  "action": "<event_type>",
  "data": { ... } // event parameters
}
```

- `action` — a string that defines the type of event/action
- `data` — a dictionary with event parameters

## Quick Start and Setup

```python
from eventrabbit import build_event_dependencies, RetryConfig

# Create decorators and event handler
retry_config = RetryConfig(max_retries=3, retry_delay_seconds=60)
events, handle = build_event_dependencies(
    url="amqp://user:password@localhost:5672/",
    idle_timeout=300,  # connection idle timeout before closing (seconds)
    retry_config=retry_config,  # retry parameters
)
```

- `url` — RabbitMQ connection string
- `idle_timeout` — connection idle timeout before automatic closing
- `retry_config` — retry parameters (default: infinite retries, 5 seconds delay)

## Using Decorators

### 1. @events.consumer

Registers an async function as a handler for incoming messages with a specific action.

```python
@events.consumer(action="USER_CREATED")
async def handle_user_created(user_id: int, name: str):
    # handle user creation event
    ...
```

- The function must accept parameters matching the keys in `data`.

### 2. @events.producer

Wraps a function so that its result is automatically sent to the queue as an event.

```python
@events.producer(exchange_name="user", action="USER_CREATED")
async def create_user(user_id: int, name: str):
    # user creation logic
    return {"user_id": user_id, "name": name}
```

- `exchange_name` — exchange for publishing the event
- `action` — event type
- `key` (optional) — routing key

### 3. @events.function

Registers a function as an event handler and automatically sends the result to the queue.

```python
@events.function(action="SEND_EMAIL", exchange_name="email", action_reply="EMAIL_SENT")
async def send_email(user_id: int, email: str):
    # email sending logic
    return {"user_id": user_id, "email": email, "status": "sent"}
```

- `action` — incoming event type
- `exchange_name` — exchange for publishing the result
- `action_reply` — event type for the reply (by default, same as action)
- `key` (optional) — routing key

## Important

- All messages must be in the format `{ "action": str, "data": dict }` — otherwise, processing will not occur.
- The library automatically manages the connection and retry logic.

## Minimal Configuration

```python
from eventrabbit import build_event_dependencies

events, handle = build_event_dependencies(
    url="amqp://user:password@localhost:5672/"
)
```

- For advanced scenarios, use the `idle_timeout`, `retry_config`, and other parameters.

---

## Queue Setup and Consumption

To consume queues, use the `ConsumeChannel` object, where you specify the queue name, exchange, and exchange type:

```python
from eventrabbit.common import ConsumeChannel
from aio_pika import ExchangeType

channel = ConsumeChannel(
    url="amqp://user:password@localhost:5672/",
    queue_name="my_queue",
    exchange_name="MY_EXCHANGE",
    exchange_type=ExchangeType.FANOUT,  # optional parameter
)

await handle.consume(channel)
```

- `exchange_type` — **optional** parameter. If not specified, the queue will be bound to the default RabbitMQ exchange.

You can run multiple queues in parallel using `asyncio.gather`:

```python
import asyncio

queues = [
    ConsumeChannel(
        url="amqp://user:password@localhost:5672/",
        queue_name="queue1",
        exchange_name="EX1",
        exchange_type=ExchangeType.FANOUT,
    ),
    ConsumeChannel(
        url="amqp://user:password@localhost:5672/",
        queue_name="queue2",
        exchange_name="EX2",
        exchange_type=ExchangeType.DIRECT,
    ),
    # You can omit exchange_type — the default exchange will be used
    ConsumeChannel(
        url="amqp://user:password@localhost:5672/",
        queue_name="queue3",
    ),
]

await asyncio.gather(*(handle.consume(ch) for ch in queues))
```

---

## reply_to Support (Response to Messages)

The library supports the **reply_to** mechanism. If the incoming message contains the `reply_to` field, the result of your function will be automatically sent back to the sender in the queue specified in `reply_to`.

- The **QueueResponse** model is used for the response, which automatically serializes the data to JSON.
- All return values of your function must be JSON-serializable (e.g., dicts, lists, strings, numbers, etc.).
- Response format: `{ "data": <your function result> }`
- This is convenient for implementing RPC over RabbitMQ.

---

## Full Example

```python
import asyncio
from aio_pika import ExchangeType
from eventrabbit import build_event_dependencies
from eventrabbit.common import ConsumeChannel

# Initialize dependencies

events, handle = build_event_dependencies(
    url="amqp://user:password@localhost:5672/",
    idle_timeout=300,
)

# Global call counter
count_call = 0

# Handler for TRACKERS_INFO event
@events.consumer(action="TRACKERS_INFO")
async def a1(b: str):
    global count_call
    print(b, "23")
    retro = Retro()
    await retro.abc()
    count_call += 1
    print("count", count_call)
    return b

# Handler for TRACKERS_INFO_1 event
@events.consumer(action="TRACKERS_INFO_1")
async def a2(b: str):
    global count_call
    print(b, "23")
    retro = Retro()
    count_call += 1
    print("count", count_call)
    await retro.abc1()
    return b

# Map of queues and exchanges
QUEUES_EXCHANGES = {
    "calendar_user_sync": "PROFILE_FANOUT_EXCHANGE",
    "calendar_google_sync": "GOOGLE_FANOUT_EXCHANGE",
    "calendar_user_status_sync": "USER_STATUS_FANOUT_EXCHANGE",
}

# Class with producers
class Retro:
    @events.producer(
        exchange_name="GOOGLE_FANOUT_EXCHANGE",
        action="TRACKERS_INFO",
    )
    async def abc(self):
        return {"b": "12"}

    @events.producer(
        exchange_name="PROFILE_FANOUT_EXCHANGE",
        action="TRACKERS_INFO_1",
    )
    async def abc1(self):
        return {"b": "12"}

# Main function to start queue consumption
async def main() -> None:
    tasks = [
        asyncio.create_task(
            handle.consume(ConsumeChannel(
                url="amqp://user:password@localhost:5672/",
                queue_name=queue,
                exchange_name=exchange,
                exchange_type=ExchangeType.FANOUT,
            )),
        )
        for queue, exchange in QUEUES_EXCHANGES.items()
    ]
    tasks += [handle.consume(ConsumeChannel(
            url="amqp://user:password@localhost:5672/",
            queue_name="tracker_info",
            exchange_type=ExchangeType.DIRECT,
        ))]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
```

---

The library does not clutter your project with unnecessary abstractions and is suitable for a concise event-driven architecture.
