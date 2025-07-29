#!/usr/bin/env python3
"""
Example demonstrating tuple component support in ABI parsing.

This example shows how to parse events with complex tuple structures,
including nested tuples and struct-like components.
"""

import json

from event_poller_sdk.abi_parser import extract_abi_event, extract_abi_events


def main():
    """Demonstrate tuple component parsing."""
    print("🔧 Event Streamer SDK - Tuple ABI Parsing Example")
    print("=" * 50)

    # Example 1: Simple tuple with basic types
    print("\n📋 Example 1: Simple Tuple Event")
    simple_tuple_abi = json.dumps(
        [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "user", "type": "address"},
                    {
                        "indexed": False,
                        "name": "data",
                        "type": "tuple",
                        "components": [
                            {"name": "amount", "type": "uint256"},
                            {"name": "token", "type": "address"},
                            {"name": "timestamp", "type": "uint256"},
                        ],
                    },
                ],
                "name": "Transfer",
                "type": "event",
            }
        ]
    )

    # Parse the ABI
    transfer_event = extract_abi_event(simple_tuple_abi, "Transfer")
    print(f"Event Name: {transfer_event.name}")
    print(f"Input Count: {len(transfer_event.inputs)}")

    # Show tuple components
    tuple_input = transfer_event.inputs[1]
    print(f"Tuple Input: {tuple_input.name} ({tuple_input.type})")
    print("Components:")
    for i, component in enumerate(tuple_input.components or []):
        print(f"  {i + 1}. {component.name}: {component.type}")

    # Example 2: Nested tuples (structs within structs)
    print("\n📋 Example 2: Nested Tuple Event")
    nested_tuple_abi = json.dumps(
        [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "orderId", "type": "uint256"},
                    {
                        "indexed": False,
                        "name": "orderData",
                        "type": "tuple",
                        "components": [
                            {"name": "maker", "type": "address"},
                            {"name": "taker", "type": "address"},
                            {
                                "name": "assets",
                                "type": "tuple",
                                "components": [
                                    {"name": "baseToken", "type": "address"},
                                    {"name": "quoteToken", "type": "address"},
                                    {"name": "baseAmount", "type": "uint256"},
                                    {"name": "quoteAmount", "type": "uint256"},
                                ],
                            },
                            {
                                "name": "fees",
                                "type": "tuple",
                                "components": [
                                    {"name": "makerFee", "type": "uint256"},
                                    {"name": "takerFee", "type": "uint256"},
                                    {"name": "protocolFee", "type": "uint256"},
                                ],
                            },
                        ],
                    },
                ],
                "name": "OrderFilled",
                "type": "event",
            }
        ]
    )

    # Parse the nested tuple ABI
    order_event = extract_abi_event(nested_tuple_abi, "OrderFilled")
    print(f"Event Name: {order_event.name}")

    # Display the nested structure
    order_data = order_event.inputs[1]
    print(f"Main Tuple: {order_data.name} ({order_data.type})")
    print("Top-level components:")

    for i, component in enumerate(order_data.components or []):
        if component.components:
            print(f"  {i + 1}. {component.name}: {component.type} (nested)")
            for j, nested_comp in enumerate(component.components):
                print(f"     {j + 1}. {nested_comp.name}: {nested_comp.type}")
        else:
            print(f"  {i + 1}. {component.name}: {component.type}")

    # Example 3: Array of tuples
    print("\n📋 Example 3: Array of Tuples Event")
    array_tuple_abi = json.dumps(
        [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "batchId", "type": "uint256"},
                    {
                        "indexed": False,
                        "name": "transfers",
                        "type": "tuple[]",  # Array of tuples
                        "components": [
                            {"name": "from", "type": "address"},
                            {"name": "to", "type": "address"},
                            {"name": "amount", "type": "uint256"},
                        ],
                    },
                ],
                "name": "BatchTransfer",
                "type": "event",
            }
        ]
    )

    batch_event = extract_abi_event(array_tuple_abi, "BatchTransfer")
    print(f"Event Name: {batch_event.name}")

    transfers_input = batch_event.inputs[1]
    print(f"Array Input: {transfers_input.name} ({transfers_input.type})")
    print("Array element components:")
    for i, component in enumerate(transfers_input.components or []):
        print(f"  {i + 1}. {component.name}: {component.type}")

    # Example 4: Extract all events from complex ABI
    print("\n📋 Example 4: Complete DeFi Protocol ABI")
    defi_abi = json.dumps(
        [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "user", "type": "address"},
                    {"indexed": True, "name": "pool", "type": "address"},
                    {
                        "indexed": False,
                        "name": "position",
                        "type": "tuple",
                        "components": [
                            {"name": "liquidity", "type": "uint128"},
                            {"name": "tickLower", "type": "int24"},
                            {"name": "tickUpper", "type": "int24"},
                            {
                                "name": "fees",
                                "type": "tuple",
                                "components": [
                                    {"name": "token0", "type": "uint256"},
                                    {"name": "token1", "type": "uint256"},
                                ],
                            },
                        ],
                    },
                ],
                "name": "PositionUpdated",
                "type": "event",
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "pool", "type": "address"},
                    {"indexed": False, "name": "sqrtPriceX96", "type": "uint160"},
                    {"indexed": False, "name": "tick", "type": "int24"},
                    {"indexed": False, "name": "liquidity", "type": "uint128"},
                ],
                "name": "PriceUpdate",
                "type": "event",
            },
        ]
    )

    # Extract all events
    all_events = extract_abi_events(defi_abi)
    print(f"Found {len(all_events)} events:")

    for event_name, event in all_events.items():
        print(f"\n  Event: {event_name}")
        for i, input_param in enumerate(event.inputs):
            if input_param.components:
                component_count = len(input_param.components)
                print(
                    f"    {i + 1}. {input_param.name}: {input_param.type} "
                    f"(tuple with {component_count} components)"
                )
            else:
                print(f"    {i + 1}. {input_param.name}: {input_param.type}")

    print("\n✅ Tuple component parsing examples completed!")
    print("\n💡 Key Features Demonstrated:")
    print("  • Simple tuple parsing with basic types")
    print("  • Nested tuple structures (structs within structs)")
    print("  • Array of tuples support")
    print("  • Complex DeFi protocol event structures")
    print("  • Recursive component validation")


if __name__ == "__main__":
    main()
