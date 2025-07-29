#!/usr/bin/env python3
"""
Example of using ABI parsing functionality in the Event Streamer SDK.

This example demonstrates how to use the SDK's ABI parsing methods to extract
ABIEvent objects from contract JSON ABI, which can then be used to create
subscriptions.
"""

from event_poller_sdk import EventStreamer

# ERC20 Token ABI (simplified for demonstration)
ERC20_ABI = """[
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "from", "type": "address"},
            {"indexed": true, "name": "to", "type": "address"},
            {"indexed": false, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "owner", "type": "address"},
            {"indexed": true, "name": "spender", "type": "address"},
            {"indexed": false, "name": "value", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "constant": false,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {"name": "owner", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]"""

# Uniswap V2 Pair ABI (events only)
UNISWAP_V2_PAIR_ABI = """[
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "sender", "type": "address"},
            {"indexed": false, "name": "amount0In", "type": "uint256"},
            {"indexed": false, "name": "amount1In", "type": "uint256"},
            {"indexed": false, "name": "amount0Out", "type": "uint256"},
            {"indexed": false, "name": "amount1Out", "type": "uint256"},
            {"indexed": true, "name": "to", "type": "address"}
        ],
        "name": "Swap",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "sender", "type": "address"},
            {"indexed": false, "name": "amount0", "type": "uint256"},
            {"indexed": false, "name": "amount1", "type": "uint256"}
        ],
        "name": "Mint",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "name": "sender", "type": "address"},
            {"indexed": false, "name": "amount0", "type": "uint256"},
            {"indexed": false, "name": "amount1", "type": "uint256"},
            {"indexed": true, "name": "to", "type": "address"}
        ],
        "name": "Burn",
        "type": "event"
    }
]"""


def demonstrate_abi_parsing():
    """Demonstrate ABI parsing functionality."""
    print("🧪 Event Streamer SDK - ABI Parsing Example")
    print("=" * 50)

    # Initialize the SDK client
    client = EventStreamer(service_url="http://localhost:8000", subscriber_id="abi-parsing-example")

    print("\n1. Extracting specific event from ERC20 ABI:")
    print("-" * 40)

    # Extract Transfer event from ERC20 ABI
    try:
        transfer_event = client.extract_abi_event(ERC20_ABI, "Transfer")
        print("✅ Successfully extracted Transfer event:")
        print(f"   Name: {transfer_event.name}")
        print(f"   Type: {transfer_event.type}")
        print(f"   Anonymous: {transfer_event.anonymous}")
        print(f"   Inputs: {len(transfer_event.inputs)}")

        for i, input_param in enumerate(transfer_event.inputs):
            print(
                f"     [{i}] {input_param.name}: {input_param.type} "
                f"(indexed: {input_param.indexed})"
            )

        print(f"\n   Topic0 (event signature): {transfer_event.name}")

    except Exception as e:
        print(f"❌ Error extracting Transfer event: {e}")

    print("\n2. Extracting all events from ERC20 ABI:")
    print("-" * 40)

    # Extract all events from ERC20 ABI
    try:
        all_events = client.extract_abi_events(ERC20_ABI)
        print(f"✅ Successfully extracted {len(all_events)} events:")

        for event_name, event_obj in all_events.items():
            print(f"   - {event_name}: {len(event_obj.inputs)} parameters")

    except Exception as e:
        print(f"❌ Error extracting all events: {e}")

    print("\n3. Parsing complete contract ABI:")
    print("-" * 40)

    # Parse complete ABI structure
    try:
        parsed_abi = client.parse_contract_abi(ERC20_ABI)
        print("✅ Successfully parsed complete ABI:")
        print(f"   Events: {len(parsed_abi['events'])}")
        print(f"   Functions: {len(parsed_abi['functions'])}")
        print(f"   Constructor: {'Yes' if parsed_abi['constructor'] else 'No'}")
        print(f"   Fallback: {'Yes' if parsed_abi['fallback'] else 'No'}")
        print(f"   Errors: {len(parsed_abi['errors'])}")

        print("\n   Available events:")
        for event_name in parsed_abi["events"].keys():
            print(f"     - {event_name}")

        print("\n   Available functions:")
        for func_name in parsed_abi["functions"].keys():
            print(f"     - {func_name}")

    except Exception as e:
        print(f"❌ Error parsing complete ABI: {e}")

    print("\n4. Working with Uniswap V2 Pair ABI:")
    print("-" * 40)

    # Extract Swap event from Uniswap V2 Pair ABI
    try:
        swap_event = client.extract_abi_event(UNISWAP_V2_PAIR_ABI, "Swap")
        print("✅ Successfully extracted Swap event:")
        print(f"   Name: {swap_event.name}")
        print(f"   Parameters: {len(swap_event.inputs)}")

        for i, input_param in enumerate(swap_event.inputs):
            indexed_str = " (indexed)" if input_param.indexed else ""
            print(f"     [{i}] {input_param.name}: {input_param.type}{indexed_str}")

    except Exception as e:
        print(f"❌ Error extracting Swap event: {e}")

    print("\n5. Error handling demonstration:")
    print("-" * 40)

    # Demonstrate error handling
    try:
        # Try to extract non-existent event
        client.extract_abi_event(ERC20_ABI, "NonExistentEvent")
    except Exception as e:
        print("✅ Correctly caught error for non-existent event:")
        print(f"   {e}")

    try:
        # Try to parse invalid JSON
        client.extract_abi_event("{invalid json}", "Transfer")
    except Exception as e:
        print("✅ Correctly caught error for invalid JSON:")
        print(f"   {e}")

    print("\n6. Practical usage - Creating subscription with parsed ABI:")
    print("-" * 40)

    # Show how to use parsed ABI in a subscription
    try:
        # Extract Transfer event for use in subscription
        transfer_event = client.extract_abi_event(ERC20_ABI, "Transfer")

        print("✅ Ready to create subscription with parsed ABI:")
        print(f"   Event: {transfer_event.name}")
        print("   Could be used in: client.create_subscription()")
        print("   Parameters:")
        print("     event_signature=transfer_event")
        print("     addresses=['0x...']")
        print("     start_block=19000000")
        print("     chain_id=1")

        # Note: Actual subscription creation would require a running service
        # subscription = await client.create_subscription(
        #     event_signature=transfer_event,
        #     addresses=["0xA0b86a33E6417b3c4555ba476F04245600306D5D"],
        #     start_block=19000000,
        #     chain_id=1
        # )

    except Exception as e:
        print(f"❌ Error in subscription demo: {e}")


def demonstrate_advanced_usage():
    """Demonstrate advanced ABI parsing features."""
    print("\n\n🚀 Advanced ABI Parsing Features")
    print("=" * 50)

    client = EventStreamer(
        service_url="http://localhost:8000", subscriber_id="advanced-abi-example"
    )

    print("\n1. Batch processing multiple ABIs:")
    print("-" * 40)

    # Process multiple contract ABIs
    contracts = {"ERC20": ERC20_ABI, "UniswapV2Pair": UNISWAP_V2_PAIR_ABI}

    all_contract_events = {}

    for contract_name, abi in contracts.items():
        try:
            events = client.extract_abi_events(abi)
            all_contract_events[contract_name] = events
            print(f"✅ {contract_name}: {len(events)} events extracted")

        except Exception as e:
            print(f"❌ Error processing {contract_name}: {e}")

    total_events = sum(len(events) for events in all_contract_events.values())
    print(f"\n   Total events across all contracts: {total_events}")

    print("\n2. Event signature analysis:")
    print("-" * 40)

    # Analyze event signatures
    for contract_name, events in all_contract_events.items():
        print(f"\n   {contract_name} events:")
        for event_name, event_obj in events.items():
            indexed_count = sum(1 for input_param in event_obj.inputs if input_param.indexed)
            non_indexed_count = len(event_obj.inputs) - indexed_count
            print(f"     - {event_name}: {indexed_count} indexed, {non_indexed_count} non-indexed")

    print("\n3. Type analysis:")
    print("-" * 40)

    # Analyze parameter types
    type_counts = {}
    for events in all_contract_events.values():
        for event_obj in events.values():
            for input_param in event_obj.inputs:
                param_type = input_param.type
                type_counts[param_type] = type_counts.get(param_type, 0) + 1

    print("   Parameter type distribution:")
    for param_type, count in sorted(type_counts.items()):
        print(f"     - {param_type}: {count} occurrences")


if __name__ == "__main__":
    """Run the ABI parsing demonstration."""
    try:
        demonstrate_abi_parsing()
        demonstrate_advanced_usage()

        print("\n\n✅ ABI Parsing Example completed successfully!")
        print("The SDK now supports automatic ABI parsing for easier event subscription creation.")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
