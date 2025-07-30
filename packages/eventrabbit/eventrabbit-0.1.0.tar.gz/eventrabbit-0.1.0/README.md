# RabbitMQ Module

A module for working with RabbitMQ in asynchronous mode. Provides convenient decorators for creating consumers, producers, and functions.

## Main Components

### 1. Factory Function (`__init__.py`)

- `build_event_dependencies()` - creates instances of decorators and event handler

### 2. Decorators (`decorators.py`)

- `EventDecorators` - class with decorators for working with RabbitMQ
- `@consumer` - decorator for creating message consumers
- `@producer` - decorator for creating message producers
- `@function` - decorator for functions with message sending

### 3. Event Handler (`queue_runtime.py`)

- `EventHandler` - main class for message processing
- `consume()` - main message consumption loop
- `process_message()` - processing incoming messages
- `handle_single_message()` - processing a single message from queue
- `handle_reply_data()` - sending responses for RPC

### 4. Connection Context (`context.py`)

- `ContextConnectionEvents` - managing connection context and handlers

### 5. Interfaces (`interface.py`)

- `IEventDecorators` - interface for decorators
- `IContextConnectionEvent` - interface for connection context
- `IRabbitQueue` - interface for queue

### 6. Data Models (`model.py`)

- `QueueDetail` - queue details
- `QueueEventType` - event types (CONSUME)
- `QueueResponse` - response model

### 7. Common Components (`common.py`)

- `ConsumeChannel` - consumption channel configuration
- `QueueData` - message data model

### 8. Connection Management (`connection.py`)

- `get_connection_rabbit()` - factory for creating connections
- Managing connection lifecycle

### 9. Queue (`queue.py`)

- `RabbitQueue` - class for working with RabbitMQ queue

## Main Features

- **Asynchronous operation** - all operations are performed asynchronously
- **Automatic reconnection** - automatically reconnects on connection errors
- **Easy to use** - convenient decorators for all types of operations
- **Convenient decorators** - simple creation of message handlers
- **Logging** - built-in logging of all operations
- **Error handling** - automatic error handling and logging
- **Connection management** - automatic management of connection lifecycle
- **Message retry system** - automatic retry mechanism with configurable delays and limits

## Decorator Types

1. **Consumer** - simple message consumer
2. **Producer** - message producer
3. **Function** - function with automatic result sending

## Message Retry System

The module includes a sophisticated message retry system that automatically handles failed message processing with configurable delays and retry limits.

### Retry Configuration

```python
from app.domain.modules.rabbit import build_event_dependencies
from app.domain.modules.rabbit.common import RetryConfig

# Configure retry settings
retry_config = RetryConfig(
    max_retries=3,              # Maximum number of retries (-1 for infinite)
    retry_delay_seconds=300     # Delay between retries in seconds (5 minutes)
)

events, handle = build_event_dependencies(
    url="amqp://user:password@localhost:5672/",
    idle_timeout=300,
    retry_config=retry_config
)
```

### How Retry System Works

1. **Message Processing**: When a message fails to process, the system automatically detects the error
2. **Retry Count Tracking**: The system tracks retry attempts using message headers (`x-retry-count`)
3. **Delay Implementation**: Uses Dead Letter Exchange pattern with TTL for delayed retries
4. **Automatic Retry**: Messages are automatically retried after the configured delay
5. **Final Rejection**: After max retries are exceeded, messages are permanently rejected

### Retry Flow

```
Message Processing Failed
         ↓
Check Retry Count < Max Retries
         ↓
Increment Retry Count in Headers
         ↓
Create Delay Queue with TTL
         ↓
Send Message to Delay Queue
         ↓
Message Returns to Main Queue After Delay
         ↓
Process Message Again
```

### Configuration Options

- **max_retries**: Maximum number of retry attempts (-1 for infinite retries)
- **retry_delay_seconds**: Time to wait between retry attempts in seconds

### Example Usage

```python
@events.consumer(action="PROCESS_EMAIL")
async def process_email(user_id: str, email_data: dict):
    try:
        # Process email logic
        result = await send_email(email_data)
        return {"status": "success", "result": result}
    except Exception as e:
        # This will trigger automatic retry with delay
        raise e  # Let the retry system handle it
```

## Configuration

The module requires URL configuration for connecting to RabbitMQ:

```python
from app.domain.modules.rabbit import build_event_dependencies

events, handle = build_event_dependencies(
    url="amqp://user:password@localhost:5672/",
    idle_timeout=300  # timeout before closing connection
)
```

## Security

- SSL connection support
- Automatic connection management
- Network error handling
- Persistent messages (delivery_mode=DeliveryMode.PERSISTENT)
- Automatic connection closing with timeout
