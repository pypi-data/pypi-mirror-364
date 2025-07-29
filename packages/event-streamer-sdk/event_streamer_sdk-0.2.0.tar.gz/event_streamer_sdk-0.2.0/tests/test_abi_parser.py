"""
Tests for ABI parsing functionality.
"""

import json

import pytest

from event_poller_sdk.abi_parser import (
    ABIParser,
    ABIParsingError,
    extract_abi_event,
    extract_abi_events,
    parse_contract_abi,
)
from event_poller_sdk.models.abi import ABIEvent, ABIInput


class TestABIParser:
    """Test cases for the ABIParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ABIParser()

        # ERC20 Transfer event
        self.transfer_event_json = {
            "type": "event",
            "name": "Transfer",
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"},
            ],
            "anonymous": False,
        }

        # ERC20 Approval event
        self.approval_event_json = {
            "type": "event",
            "name": "Approval",
            "inputs": [
                {"indexed": True, "name": "owner", "type": "address"},
                {"indexed": True, "name": "spender", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"},
            ],
            "anonymous": False,
        }

        # ERC20 function
        self.transfer_function_json = {
            "type": "function",
            "name": "transfer",
            "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}],
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
        }

        # Complete ERC20 ABI
        self.erc20_abi = [
            self.transfer_event_json,
            self.approval_event_json,
            self.transfer_function_json,
        ]

    def test_parse_abi_json_success(self):
        """Test successful ABI JSON parsing."""
        abi_json = json.dumps(self.erc20_abi)
        result = self.parser.parse_abi_json(abi_json)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["type"] == "event"
        assert result[0]["name"] == "Transfer"

    def test_parse_abi_json_invalid_json(self):
        """Test ABI JSON parsing with invalid JSON."""
        with pytest.raises(ABIParsingError, match="Invalid JSON in ABI"):
            self.parser.parse_abi_json("{invalid json}")

    def test_parse_abi_json_not_array(self):
        """Test ABI JSON parsing with non-array JSON."""
        with pytest.raises(ABIParsingError, match="ABI must be a JSON array"):
            self.parser.parse_abi_json('{"type": "event"}')

    def test_parse_abi_json_empty_array(self):
        """Test ABI JSON parsing with empty array."""
        with pytest.raises(ABIParsingError, match="ABI cannot be empty"):
            self.parser.parse_abi_json("[]")

    def test_parse_abi_json_invalid_element(self):
        """Test ABI JSON parsing with invalid element."""
        with pytest.raises(ABIParsingError, match="ABI element .* must be an object"):
            self.parser.parse_abi_json('["not an object"]')

    def test_parse_abi_json_missing_type(self):
        """Test ABI JSON parsing with missing type field."""
        with pytest.raises(ABIParsingError, match="ABI element .* missing 'type' field"):
            self.parser.parse_abi_json('[{"name": "test"}]')

    def test_extract_events_from_abi_success(self):
        """Test successful event extraction from ABI."""
        events = self.parser.extract_events_from_abi(self.erc20_abi)

        assert "Transfer" in events
        assert "Approval" in events
        assert len(events) == 2

        transfer_event = events["Transfer"]
        assert transfer_event["name"] == "Transfer"
        assert len(transfer_event["inputs"]) == 3

    def test_extract_events_from_abi_no_events(self):
        """Test event extraction from ABI with no events."""
        abi_with_no_events = [self.transfer_function_json]
        events = self.parser.extract_events_from_abi(abi_with_no_events)

        assert len(events) == 0

    def test_extract_events_from_abi_duplicate_names(self):
        """Test event extraction with duplicate event names."""
        abi_with_duplicates = [
            self.transfer_event_json,
            self.transfer_event_json,  # Duplicate
        ]

        with pytest.raises(ABIParsingError, match="Duplicate event name: Transfer"):
            self.parser.extract_events_from_abi(abi_with_duplicates)

    def test_extract_events_from_abi_missing_name(self):
        """Test event extraction with missing event name."""
        event_without_name = {"type": "event", "inputs": []}

        with pytest.raises(ABIParsingError, match="Event definition missing 'name' field"):
            self.parser.extract_events_from_abi([event_without_name])

    def test_extract_events_from_abi_invalid_name_type(self):
        """Test event extraction with invalid event name type."""
        event_invalid_name = {
            "type": "event",
            "name": 123,  # Should be string
            "inputs": [],
        }

        with pytest.raises(ABIParsingError, match="Event name must be a string"):
            self.parser.extract_events_from_abi([event_invalid_name])

    def test_validate_event_structure_success(self):
        """Test successful event structure validation."""
        # Should not raise any exception
        self.parser._validate_event_structure(self.transfer_event_json)

    def test_validate_event_structure_invalid_inputs(self):
        """Test event structure validation with invalid inputs."""
        invalid_event = {"type": "event", "name": "Test", "inputs": "not an array"}

        with pytest.raises(ABIParsingError, match="Event 'inputs' must be an array"):
            self.parser._validate_event_structure(invalid_event)

    def test_validate_event_structure_invalid_input_object(self):
        """Test event structure validation with invalid input object."""
        invalid_event = {"type": "event", "name": "Test", "inputs": ["not an object"]}

        with pytest.raises(ABIParsingError, match="Event input .* must be an object"):
            self.parser._validate_event_structure(invalid_event)

    def test_validate_event_structure_missing_input_type(self):
        """Test event structure validation with missing input type."""
        invalid_event = {
            "type": "event",
            "name": "Test",
            "inputs": [{"name": "test"}],  # Missing type
        }

        with pytest.raises(ABIParsingError, match="Event input .* missing 'type' field"):
            self.parser._validate_event_structure(invalid_event)

    def test_validate_event_structure_invalid_input_type(self):
        """Test event structure validation with invalid input type."""
        invalid_event = {
            "type": "event",
            "name": "Test",
            "inputs": [{"name": "test", "type": 123}],  # Type should be string
        }

        with pytest.raises(ABIParsingError, match="Event input .* 'type' must be a string"):
            self.parser._validate_event_structure(invalid_event)

    def test_validate_event_structure_invalid_indexed_type(self):
        """Test event structure validation with invalid indexed type."""
        invalid_event = {
            "type": "event",
            "name": "Test",
            "inputs": [{"name": "test", "type": "uint256", "indexed": "not boolean"}],
        }

        with pytest.raises(ABIParsingError, match="Event input .* 'indexed' must be a boolean"):
            self.parser._validate_event_structure(invalid_event)

    def test_validate_event_structure_invalid_name_type(self):
        """Test event structure validation with invalid name type."""
        invalid_event = {
            "type": "event",
            "name": "Test",
            "inputs": [{"name": 123, "type": "uint256"}],  # Name should be string
        }

        with pytest.raises(ABIParsingError, match="Event input .* 'name' must be a string"):
            self.parser._validate_event_structure(invalid_event)

    def test_convert_to_abi_event_success(self):
        """Test successful conversion to ABIEvent."""
        abi_event = self.parser.convert_to_abi_event(self.transfer_event_json)

        assert isinstance(abi_event, ABIEvent)
        assert abi_event.name == "Transfer"
        assert abi_event.type == "event"
        assert not abi_event.anonymous
        assert len(abi_event.inputs) == 3

        # Check first input
        first_input = abi_event.inputs[0]
        assert isinstance(first_input, ABIInput)
        assert first_input.name == "from"
        assert first_input.type == "address"
        assert first_input.indexed

    def test_convert_to_abi_event_conversion_failure(self):
        """Test conversion to ABIEvent with invalid data."""
        invalid_event = {
            "name": "Test",
            "inputs": [{"type": "invalid_type"}],  # Invalid Solidity type
        }

        with pytest.raises(ABIParsingError, match="Failed to convert event"):
            self.parser.convert_to_abi_event(invalid_event)

    def test_extract_abi_event_success(self):
        """Test successful extraction of specific event."""
        abi_json = json.dumps(self.erc20_abi)
        abi_event = self.parser.extract_abi_event(abi_json, "Transfer")

        assert isinstance(abi_event, ABIEvent)
        assert abi_event.name == "Transfer"
        assert len(abi_event.inputs) == 3

    def test_extract_abi_event_not_found(self):
        """Test extraction of non-existent event."""
        abi_json = json.dumps(self.erc20_abi)

        with pytest.raises(ABIParsingError, match="Event 'NonExistent' not found in ABI"):
            self.parser.extract_abi_event(abi_json, "NonExistent")

    def test_extract_abi_events_success(self):
        """Test successful extraction of all events."""
        abi_json = json.dumps(self.erc20_abi)
        events = self.parser.extract_abi_events(abi_json)

        assert len(events) == 2
        assert "Transfer" in events
        assert "Approval" in events
        assert isinstance(events["Transfer"], ABIEvent)
        assert isinstance(events["Approval"], ABIEvent)

    def test_parse_contract_abi_success(self):
        """Test successful parsing of complete contract ABI."""
        abi_json = json.dumps(self.erc20_abi)
        result = self.parser.parse_contract_abi(abi_json)

        assert "events" in result
        assert "functions" in result
        assert "constructor" in result
        assert "fallback" in result
        assert "receive" in result
        assert "errors" in result
        assert "raw" in result

        # Check events
        assert len(result["events"]) == 2
        assert "Transfer" in result["events"]
        assert "Approval" in result["events"]

        # Check functions
        assert len(result["functions"]) == 1
        assert "transfer" in result["functions"]
        assert isinstance(result["functions"]["transfer"], list)

        # Check raw data
        assert result["raw"] == self.erc20_abi


class TestConvenienceFunctions:
    """Test cases for the convenience functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.erc20_abi_json = json.dumps(
            [
                {
                    "type": "event",
                    "name": "Transfer",
                    "inputs": [
                        {"indexed": True, "name": "from", "type": "address"},
                        {"indexed": True, "name": "to", "type": "address"},
                        {"indexed": False, "name": "value", "type": "uint256"},
                    ],
                    "anonymous": False,
                }
            ]
        )

    def test_extract_abi_event_convenience(self):
        """Test the convenience extract_abi_event function."""
        abi_event = extract_abi_event(self.erc20_abi_json, "Transfer")

        assert isinstance(abi_event, ABIEvent)
        assert abi_event.name == "Transfer"

    def test_extract_abi_events_convenience(self):
        """Test the convenience extract_abi_events function."""
        events = extract_abi_events(self.erc20_abi_json)

        assert len(events) == 1
        assert "Transfer" in events
        assert isinstance(events["Transfer"], ABIEvent)

    def test_parse_contract_abi_convenience(self):
        """Test the convenience parse_contract_abi function."""
        result = parse_contract_abi(self.erc20_abi_json)

        assert "events" in result
        assert len(result["events"]) == 1
        assert "Transfer" in result["events"]


class TestRealWorldABI:
    """Test cases with real-world ABI examples."""

    def test_uniswap_v2_pair_abi(self):
        """Test with Uniswap V2 Pair ABI."""
        uniswap_abi = """[
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
                "anonymous": false,
                "inputs": [
                    {"indexed": true, "name": "sender", "type": "address"},
                    {"indexed": false, "name": "amount0", "type": "uint256"},
                    {"indexed": false, "name": "amount1", "type": "uint256"},
                    {"indexed": true, "name": "to", "type": "address"}
                ],
                "name": "Burn",
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
                    {"indexed": false, "name": "reserve0", "type": "uint112"},
                    {"indexed": false, "name": "reserve1", "type": "uint112"}
                ],
                "name": "Sync",
                "type": "event"
            },
            {
                "anonymous": false,
                "inputs": [
                    {"indexed": true, "name": "from", "type": "address"},
                    {"indexed": true, "name": "to", "type": "address"},
                    {"indexed": false, "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            }
        ]"""

        # Test extracting specific event
        swap_event = extract_abi_event(uniswap_abi, "Swap")
        assert swap_event.name == "Swap"
        assert len(swap_event.inputs) == 6

        # Test extracting all events
        all_events = extract_abi_events(uniswap_abi)
        assert len(all_events) == 6
        assert "Swap" in all_events
        assert "Transfer" in all_events
        assert "Approval" in all_events
        assert "Burn" in all_events
        assert "Mint" in all_events
        assert "Sync" in all_events

    def test_erc721_abi(self):
        """Test with ERC721 ABI."""
        erc721_abi = """[
            {
                "anonymous": false,
                "inputs": [
                    {"indexed": true, "name": "owner", "type": "address"},
                    {"indexed": true, "name": "approved", "type": "address"},
                    {"indexed": true, "name": "tokenId", "type": "uint256"}
                ],
                "name": "Approval",
                "type": "event"
            },
            {
                "anonymous": false,
                "inputs": [
                    {"indexed": true, "name": "owner", "type": "address"},
                    {"indexed": true, "name": "operator", "type": "address"},
                    {"indexed": false, "name": "approved", "type": "bool"}
                ],
                "name": "ApprovalForAll",
                "type": "event"
            },
            {
                "anonymous": false,
                "inputs": [
                    {"indexed": true, "name": "from", "type": "address"},
                    {"indexed": true, "name": "to", "type": "address"},
                    {"indexed": true, "name": "tokenId", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            }
        ]"""

        # Test extracting Transfer event
        transfer_event = extract_abi_event(erc721_abi, "Transfer")
        assert transfer_event.name == "Transfer"
        assert len(transfer_event.inputs) == 3

        # Verify indexed fields
        assert transfer_event.inputs[0].indexed  # from
        assert transfer_event.inputs[1].indexed  # to
        assert transfer_event.inputs[2].indexed  # tokenId

    def test_complex_abi_with_tuples(self):
        """Test with ABI containing tuple types."""
        complex_abi = """[
            {
                "anonymous": false,
                "inputs": [
                    {"indexed": false, "name": "id", "type": "uint256"},
                    {
                        "indexed": false,
                        "name": "data",
                        "type": "tuple",
                        "components": [
                            {"name": "amount", "type": "uint256"},
                            {"name": "token", "type": "address"}
                        ]
                    }
                ],
                "name": "ComplexEvent",
                "type": "event"
            }
        ]"""

        # Test extracting event with tuple
        complex_event = extract_abi_event(complex_abi, "ComplexEvent")
        assert complex_event.name == "ComplexEvent"
        assert len(complex_event.inputs) == 2

        # Check tuple input
        tuple_input = complex_event.inputs[1]
        assert tuple_input.type == "tuple"
        assert tuple_input.name == "data"

        # Verify components are properly parsed
        assert tuple_input.components is not None
        assert len(tuple_input.components) == 2

        # Check first component
        amount_component = tuple_input.components[0]
        assert amount_component.name == "amount"
        assert amount_component.type == "uint256"
        assert amount_component.components is None

        # Check second component
        token_component = tuple_input.components[1]
        assert token_component.name == "token"
        assert token_component.type == "address"
        assert token_component.components is None

    def test_nested_tuple_abi(self):
        """Test with ABI containing nested tuple types."""
        nested_tuple_abi = """[
            {
                "anonymous": false,
                "inputs": [
                    {"indexed": false, "name": "id", "type": "uint256"},
                    {
                        "indexed": false,
                        "name": "nestedData",
                        "type": "tuple",
                        "components": [
                            {"name": "user", "type": "address"},
                            {
                                "name": "userInfo",
                                "type": "tuple",
                                "components": [
                                    {"name": "balance", "type": "uint256"},
                                    {"name": "isActive", "type": "bool"}
                                ]
                            }
                        ]
                    }
                ],
                "name": "NestedEvent",
                "type": "event"
            }
        ]"""

        # Test extracting event with nested tuple
        nested_event = extract_abi_event(nested_tuple_abi, "NestedEvent")
        assert nested_event.name == "NestedEvent"
        assert len(nested_event.inputs) == 2

        # Check nested tuple input
        nested_tuple_input = nested_event.inputs[1]
        assert nested_tuple_input.type == "tuple"
        assert nested_tuple_input.name == "nestedData"
        assert nested_tuple_input.components is not None
        assert len(nested_tuple_input.components) == 2

        # Check first component (simple type)
        user_component = nested_tuple_input.components[0]
        assert user_component.name == "user"
        assert user_component.type == "address"
        assert user_component.components is None

        # Check second component (nested tuple)
        user_info_component = nested_tuple_input.components[1]
        assert user_info_component.name == "userInfo"
        assert user_info_component.type == "tuple"
        assert user_info_component.components is not None
        assert len(user_info_component.components) == 2

        # Check nested tuple components
        balance_component = user_info_component.components[0]
        assert balance_component.name == "balance"
        assert balance_component.type == "uint256"
        assert balance_component.components is None

        is_active_component = user_info_component.components[1]
        assert is_active_component.name == "isActive"
        assert is_active_component.type == "bool"
        assert is_active_component.components is None

    def test_tuple_validation_errors(self):
        """Test validation errors for tuple components."""

        # Test invalid components structure (not an array)
        invalid_components_abi = """[
            {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": false,
                        "name": "data",
                        "type": "tuple",
                        "components": "not an array"
                    }
                ],
                "name": "InvalidEvent",
                "type": "event"
            }
        ]"""

        with pytest.raises(ABIParsingError, match="components must be an array"):
            extract_abi_event(invalid_components_abi, "InvalidEvent")

        # Test component missing type
        missing_type_abi = """[
            {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": false,
                        "name": "data",
                        "type": "tuple",
                        "components": [
                            {"name": "value"}
                        ]
                    }
                ],
                "name": "InvalidEvent",
                "type": "event"
            }
        ]"""

        with pytest.raises(ABIParsingError, match="component 0 missing 'type' field"):
            extract_abi_event(missing_type_abi, "InvalidEvent")

        # Test component with invalid type
        invalid_type_abi = """[
            {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": false,
                        "name": "data",
                        "type": "tuple",
                        "components": [
                            {"name": "value", "type": 123}
                        ]
                    }
                ],
                "name": "InvalidEvent",
                "type": "event"
            }
        ]"""

        with pytest.raises(ABIParsingError, match="component 0 'type' must be a string"):
            extract_abi_event(invalid_type_abi, "InvalidEvent")
