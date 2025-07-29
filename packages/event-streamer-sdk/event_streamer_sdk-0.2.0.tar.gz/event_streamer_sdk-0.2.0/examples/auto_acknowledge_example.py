"""
Example: Using Event Streamer SDK with Auto-Acknowledgment

This example demonstrates how to use the auto-acknowledgment feature
to automatically acknowledge events after successful handler execution.
It also shows how to extract ABIEvent objects from contract ABI JSON.
"""

import asyncio

from event_poller_sdk import EventStreamer
from event_poller_sdk.models.subscriptions import SubscriptionCreate

# Example ERC20 contract ABI (partial)
ERC20_ABI = """[
    {
        "type": "event",
        "name": "Transfer",
        "inputs": [
            {"indexed": true, "name": "from", "type": "address"},
            {"indexed": true, "name": "to", "type": "address"},
            {"indexed": false, "name": "value", "type": "uint256"}
        ]
    },
    {
        "type": "event",
        "name": "Approval",
        "inputs": [
            {"indexed": true, "name": "owner", "type": "address"},
            {"indexed": true, "name": "spender", "type": "address"},
            {"indexed": false, "name": "value", "type": "uint256"}
        ]
    }
]"""


async def main():
    """Main example function."""

    # Initialize the EventStreamer client
    async with EventStreamer(
        # TODO: add default URL configuration (DCE-47)
        service_url="http://localhost:1337",
        # TODO: document subscriber ID provisioning process (DCE-51)
        subscriber_id="auto-ack-example",
    ) as client:
        # Extract the Transfer event from the ABI
        # This is the new helper method that was requested in the TODO
        transfer_event = client.extract_abi_event(ERC20_ABI, "Transfer")
        print(f"✅ Extracted Transfer event: {transfer_event.name}")

        # You can also extract all events at once
        all_events = client.extract_abi_events(ERC20_ABI)
        print(f"📋 Found {len(all_events)} events in ABI: {list(all_events.keys())}")

        # Create a subscription for live Transfer events
        print("📝 Creating subscription for live Transfer events...")
        subscription = SubscriptionCreate(
            topic0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            event_signature=transfer_event,
            addresses=[],
            start_block=22938015,
            end_block=None,  # Live monitoring
            chain_id=1,  # Ethereum mainnet
            subscriber_id="auto-ack-example",
        )

        result = await client.create_subscription(subscription)
        print(f"✅ Created subscription with ID: {result.id}")

        # Create streaming client with auto-acknowledgment enabled
        streaming_client = client.create_streaming_client(
            subscription_id=result.id,
            client_metadata={"client_version": "1.0.0", "example": "auto-acknowledge"},
            auto_acknowledge=True,  # Enable auto-acknowledgment
        )

        # Register event handlers - NO MANUAL ACKNOWLEDGMENT NEEDED!
        @streaming_client.on_event("Transfer")
        async def handle_transfer_events(events):
            """Handle Transfer events - auto-acknowledged on success."""
            print(f"🔄 Received {len(events)} Transfer events:")
            for event in events:
                from_addr = event["from"][:6] + "..." + event["from"][-4:]
                to_addr = event["to"][:6] + "..." + event["to"][-4:]
                print(f"  💰 {from_addr} → {to_addr}: {event['value']} tokens")
                print(f"    📦 Block: {event['block_number']}")
                print(f"    ✅ Auto-acknowledged: {event['transaction_hash']}:{event['log_index']}")
                # No manual acknowledgment needed - handled automatically!

        @streaming_client.on_event("Approval")
        async def handle_approval_events(events):
            """Handle Approval events - auto-acknowledged on success."""
            print(f"✅ Received {len(events)} Approval events:")
            for event in events:
                owner = event["owner"][:6] + "..." + event["owner"][-4:]
                spender = event["spender"][:6] + "..." + event["spender"][-4:]
                print(f"  🔑 {owner} approved {spender}: {event['value']} tokens")
                print(f"    ✅ Auto-acknowledged: {event['transaction_hash']}:{event['log_index']}")
                # No manual acknowledgment needed - handled automatically!

        # Global handler for comprehensive event logging
        @streaming_client.on_all_events
        async def handle_all_events(events):
            """Log all events for monitoring."""
            total_events = sum(len(event_list) for event_list in events.values())
            if total_events > 0:
                print(f"📊 Total events received: {total_events}")
                for event_name, event_list in events.items():
                    print(f"  - {event_name}: {len(event_list)} events")

        # Optional: Handle heartbeats
        @streaming_client.on_heartbeat
        async def handle_heartbeat(heartbeat):
            """Handle heartbeat messages."""
            print(f"💓 Heartbeat received: {heartbeat.timestamp}")

        # Optional: Handle errors
        @streaming_client.on_error
        async def handle_error(error):
            """Handle error messages."""
            print(f"❌ Streaming error: {error.error_message}")

        # Start streaming
        print("🚀 Starting streaming client with auto-acknowledgment...")
        await streaming_client.start_streaming()

        print(f"⛓️  Monitoring chain: {subscription.chain_id}")
        print("📍 Contract: All contracts")
        print(f"🔄 Resume token: {streaming_client.get_current_resume_token()}")

        print("\n🎯 Streaming client is running with AUTO-ACKNOWLEDGMENT enabled!")
        print("📺 Events will be automatically acknowledged after successful processing")
        print("🛑 Press Ctrl+C to stop...\n")

        # Keep the client running
        try:
            while streaming_client.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping streaming client...")
        finally:
            await streaming_client.disconnect()
            print("👋 Streaming client stopped")


if __name__ == "__main__":
    asyncio.run(main())
