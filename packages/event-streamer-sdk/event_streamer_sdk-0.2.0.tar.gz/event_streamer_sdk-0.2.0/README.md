# Event Streamer SDK

A Python SDK for interacting with the Event Streamer blockchain event monitoring service. This SDK provides a simple and powerful way to subscribe to blockchain events and receive them via HTTP streaming connections.

## Features

- 🔗 **Simple API Client**: Easy subscription management with typed responses
- 🌊 **HTTP Streaming**: Real-time event delivery via HTTP streaming connections
- 🔄 **Resume Capability**: Automatic resume from last processed position
- 🔒 **Type Safety**: Full type hints and Pydantic model validation
- ⚡ **Async/Await**: Modern async Python patterns throughout
- 🎯 **Decorator Pattern**: Clean event handler registration
- 🛡️ **Error Handling**: Comprehensive error handling and connection management
- 💓 **Health Monitoring**: Built-in heartbeat and connection health tracking
- 📝 **ABI Parsing**: Built-in contract ABI parsing for easy event extraction
- 🔮 **Future-Ready**: Prepared for authentication when the service adds it

## Installation

```bash
pip install event-streamer-sdk
```

## Quick Start

### HTTP Streaming Example

```python
import asyncio
from event_poller_sdk import EventStreamer
from event_poller_sdk.models.subscriptions import SubscriptionCreate
from event_poller_sdk.models.abi import ABIEvent, ABIInput

async def main():
    # Initialize the client
    async with EventStreamer(
        service_url="http://localhost:8000",
        subscriber_id="my-app"
    ) as client:

        # Create a subscription
        subscription = SubscriptionCreate(
            topic0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            event_signature=ABIEvent(
                type="event",
                name="Transfer",
                inputs=[
                    ABIInput(name="from", type="address", indexed=True),
                    ABIInput(name="to", type="address", indexed=True),
                    ABIInput(name="value", type="uint256", indexed=False)
                ]
            ),
            addresses=["0xA0b86a33E6417b3c4555ba476F04245600306D5D"],
            start_block=19000000,
            end_block=19010000,
            chain_id=1,
            subscriber_id="my-app"
        )

        result = await client.create_subscription(subscription)
        print(f"Created subscription: {result.id}")

        # Create streaming client
        streaming_client = client.create_streaming_client(
            subscription_id=result.id,
            client_metadata={"version": "1.0.0"}
        )

        # Register event handlers
        @streaming_client.on_event("Transfer")
        async def handle_transfers(events):
            for event in events:
                print(f"Transfer: {event['from']} -> {event['to']}: {event['value']}")

        # Start streaming
        await streaming_client.start_streaming()

        # Keep running to receive events
        try:
            while streaming_client.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            await streaming_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Resume Capability Example

```python
import asyncio
from event_poller_sdk import EventStreamer

async def main():
    async with EventStreamer(
        service_url="http://localhost:8000",
        subscriber_id="my-app"
    ) as client:

        # Create streaming client with resume token
        streaming_client = client.create_streaming_client(
            subscription_id=123,
            resume_token="rt_eyJzdWJzY3JpcHRpb25faWQiOjEyMywi...",
            client_metadata={"version": "1.0.0"}
        )

        @streaming_client.on_event("Transfer")
        async def handle_transfers(events):
            for event in events:
                print(f"Transfer: {event['from']} -> {event['to']}: {event['value']}")

        # Optional: Handle heartbeats
        @streaming_client.on_heartbeat
        async def handle_heartbeat(heartbeat):
            print(f"Heartbeat: {heartbeat.timestamp}")

        # Optional: Handle errors
        @streaming_client.on_error
        async def handle_error(error):
            print(f"Error: {error.error_message}")

        # Start streaming
        await streaming_client.start_streaming()

        # Keep running and save resume token periodically
        try:
            while streaming_client.is_running:
                current_token = streaming_client.get_current_resume_token()
                # Save token to persistent storage
                await asyncio.sleep(30)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            await streaming_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## ABI Parsing

The SDK includes built-in ABI parsing functionality to make it easy to extract event definitions from contract ABIs without manually constructing `ABIEvent` objects.

### Extract Specific Event

```python
async def main():
    async with EventStreamer(
        service_url="http://localhost:8000",
        subscriber_id="my-app"
    ) as client:

        # Example ERC20 contract ABI
        erc20_abi = '''[
            {
                "type": "event",
                "name": "Transfer",
                "inputs": [
                    {"indexed": true, "name": "from", "type": "address"},
                    {"indexed": true, "name": "to", "type": "address"},
                    {"indexed": false, "name": "value", "type": "uint256"}
                ]
            }
        ]'''

        # Extract the Transfer event
        transfer_event = client.extract_abi_event(erc20_abi, "Transfer")

        # Use in subscription
        subscription = SubscriptionCreate(
            topic0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            event_signature=transfer_event,  # Use parsed event
            addresses=["0x..."],
            start_block=19000000,
            chain_id=1
        )
```

### Extract All Events

```python
# Extract all events from an ABI
all_events = client.extract_abi_events(erc20_abi)
transfer_event = all_events["Transfer"]
approval_event = all_events["Approval"]
```

### Error Handling

```python
try:
    event = client.extract_abi_event(abi_json, "NonExistentEvent")
except Exception as e:
    print(f"Event not found: {e}")
    # Error message includes available events
```

### Supported ABI Features

- ✅ **Event definitions**: Full support for event parsing
- ✅ **Indexed parameters**: Correctly handles indexed/non-indexed inputs
- ✅ **Array types**: Supports `uint256[]`, `address[]`, etc.
- ✅ **Anonymous events**: Handles anonymous event flag
- ✅ **Complex types**: Support for most Solidity types
- ✅ **Error handling**: Clear error messages with available events
- ⚠️ **Tuple components**: Basic support (see TODO in DCE-50)

## API Reference

### EventStreamer

The main client class for interacting with the Event Streamer service.

```python
class EventStreamer:
    def __init__(
        self,
        service_url: str,
        subscriber_id: str,
        timeout: int = 30,
        api_key: Optional[str] = None,  # Future use
        auth_token: Optional[str] = None,  # Future use
    )
```

#### Subscription Management

```python
# Create a subscription
async def create_subscription(self, subscription: SubscriptionCreate) -> SubscriptionResponse

# List subscriptions
async def list_subscriptions(self, page: int = 1, page_size: int = 20) -> SubscriptionListResponse

# Get a specific subscription
async def get_subscription(self, subscription_id: int) -> SubscriptionResponse

# Update a subscription
async def update_subscription(self, subscription_id: int, update: SubscriptionUpdate) -> SubscriptionResponse

# Delete a subscription
async def delete_subscription(self, subscription_id: int) -> bool
```

#### Streaming Client Creation

```python
# Create a streaming client for a subscription
def create_streaming_client(
    self,
    subscription_id: int,
    resume_token: Optional[str] = None,
    client_metadata: Optional[Dict[str, Any]] = None
) -> StreamingClient
```

### StreamingClient

The streaming client handles real-time event delivery via HTTP streaming connections.

#### Connection Management

```python
# Connect to streaming endpoint
async def connect() -> None

# Start streaming events
async def start_streaming() -> None

# Stop streaming events
async def stop_streaming() -> None

# Disconnect from streaming
async def disconnect() -> None

# Resume from a specific position
async def resume(resume_token: str) -> None

# Get current resume token
def get_current_resume_token() -> Optional[str]
```

#### Event Handler Registration

```python
# Handle specific event types
@client.on_event("Transfer")
async def handle_transfers(events: List[Dict[str, Any]]):
    for event in events:
        # Process event
        pass

# Handle all events
@client.on_all_events
async def handle_all_events(events: Dict[str, List[Dict[str, Any]]]):
    for event_name, event_list in events.items():
        # Process events by type
        pass

# Handle heartbeat messages
@client.on_heartbeat
async def handle_heartbeat(heartbeat: StreamingHeartbeat):
    print(f"Heartbeat: {heartbeat.timestamp}")

# Handle error messages
@client.on_error
async def handle_error(error: StreamingError):
    print(f"Error: {error.error_message}")
```

### Models

#### SubscriptionCreate

```python
class SubscriptionCreate(BaseModel):
    topic0: str                    # Event signature hash
    event_signature: ABIEvent      # ABI event definition
    addresses: List[str] = []      # Contract addresses (empty = all)
    start_block: int               # Starting block number
    end_block: Optional[int] = None # Ending block (None = live)
    chain_id: int                  # Blockchain network ID
    subscriber_id: str             # Your service identifier
```

#### ABIEvent

```python
class ABIEvent(BaseModel):
    type: Literal["event"]
    name: str                      # Event name
    inputs: List[ABIInput] = []    # Event parameters
    anonymous: bool = False
```

#### ABIInput

```python
class ABIInput(BaseModel):
    name: Optional[str] = None     # Parameter name
    type: str                      # Solidity type (e.g., "address", "uint256")
    indexed: Optional[bool] = False # Whether parameter is indexed
```

## Event Data Format

Events are delivered via streaming in batches with the following format:

```python
{
    "type": "event_batch",
    "response_id": "550e8400-e29b-41d4-a716-446655440000",
    "subscription_id": 123,
    "connection_id": "conn_550e8400-e29b-41d4-a716-446655440000",
    "resume_token": "rt_eyJzdWJzY3JpcHRpb25faWQiOjEyMywi...",
    "events": {
        "Transfer": [
            {
                # Event-specific fields
                "from": "0x1234567890123456789012345678901234567890",
                "to": "0x0987654321098765432109876543210987654321",
                "value": "1000000000000000000",

                # Metadata fields
                "block_number": 19000001,
                "transaction_hash": "0xabcdef...",
                "log_index": 0,
                "address": "0xA0b86a33E6417b3c4555ba476F04245600306D5D",
                "timestamp": "2024-05-23T10:30:00.000Z"
            }
        ]
    },
    "batch_size": 1,
    "timestamp": "2024-05-23T10:30:00.000Z"
}
```

### Streaming Message Types

The streaming connection delivers different types of messages:

#### Event Batch
Contains actual blockchain events for processing.

#### Heartbeat
Periodic heartbeat messages to maintain connection health:
```python
{
    "type": "heartbeat",
    "connection_id": "conn_550e8400-e29b-41d4-a716-446655440000",
    "subscription_id": 123,
    "timestamp": "2024-05-23T10:30:00.000Z"
}
```

#### Error Messages
Error notifications and connection issues:
```python
{
    "type": "error",
    "connection_id": "conn_550e8400-e29b-41d4-a716-446655440000",
    "subscription_id": 123,
    "error_code": "CONNECTION_LOST",
    "error_message": "Connection lost due to network timeout",
    "timestamp": "2024-05-23T10:30:00.000Z"
}
```

## Supported Chains

The SDK supports all chains configured in your Event Streamer service:

- **Ethereum Mainnet** (Chain ID: 1)
- **Polygon** (Chain ID: 137)
- **Base** (Chain ID: 8453)
- **Arbitrum One** (Chain ID: 42161)
- **Optimism** (Chain ID: 10)

## Error Handling

The SDK provides comprehensive error handling:

```python
from event_poller_sdk.exceptions import (
    EventPollerSDKError,           # Base exception
    EventPollerConnectionError,    # Connection issues
    EventPollerTimeoutError,       # Request timeouts
    EventPollerValidationError,    # Validation errors
    EventPollerSubscriptionError,  # Subscription errors
)

try:
    subscription = await client.create_subscription(subscription_data)
except EventPollerValidationError as e:
    print(f"Invalid subscription data: {e}")
except EventPollerConnectionError as e:
    print(f"Connection failed: {e}")
```

## Best Practices

### 1. Use Context Managers

Always use the EventStreamer as an async context manager to ensure proper cleanup:

```python
async with EventStreamer(service_url, subscriber_id) as client:
    # Your code here
    pass
```

### 2. Handle Events Efficiently

Process events quickly in your handlers to avoid blocking the streaming connection:

```python
@client.on_event("Transfer")
async def handle_transfers(events):
    # Process quickly to avoid blocking
    for event in events:
        await process_event_async(event)
```

### 3. Use Specific Event Handlers

Register handlers for specific event types rather than using only the global handler:

```python
@client.on_event("Transfer")
async def handle_transfers(events):
    # Specific handling for transfers
    pass

@client.on_event("Approval")
async def handle_approvals(events):
    # Specific handling for approvals
    pass
```

### 4. Implement Resume Token Persistence

Save resume tokens to persistent storage to resume from the correct position after restarts:

```python
# Save resume token periodically
resume_token = streaming_client.get_current_resume_token()
await save_resume_token_to_storage(subscription_id, resume_token)

# Resume from saved position
saved_token = await load_resume_token_from_storage(subscription_id)
streaming_client = client.create_streaming_client(
    subscription_id=subscription_id,
    resume_token=saved_token
)
```

### 5. Handle Connection Errors Gracefully

Implement proper error handling for connection issues:

```python
@client.on_error
async def handle_error(error):
    if error.error_code == "CONNECTION_LOST":
        # Implement reconnection logic
        await reconnect_with_backoff()
    else:
        # Log and handle other errors
        logger.error(f"Streaming error: {error.error_message}")
```

### 6. Monitor Connection Health

Use heartbeat handlers to monitor connection health:

```python
@client.on_heartbeat
async def handle_heartbeat(heartbeat):
    # Update last heartbeat time
    last_heartbeat = heartbeat.timestamp
    # Check connection health
    await update_connection_health_metrics()
```

## Development

### Requirements

- Python 3.11+
- aiohttp
- pydantic
- eth-typing
- event-poller-schemas

### Installation for Development

```bash
git clone https://github.com/dcentralab/event-poller-sdk
cd event-poller-sdk
pip install -e ".[dev]"
```

### Running Examples

```bash
# Live streaming example
python examples/streaming_example.py

# Historical streaming example
python examples/historical_streaming_example.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
