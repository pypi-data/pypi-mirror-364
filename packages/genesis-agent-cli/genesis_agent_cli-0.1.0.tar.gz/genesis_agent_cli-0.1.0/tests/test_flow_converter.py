"""
Unit tests for the Flow Converter module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json

from src.converters.flow_converter import FlowConverter
from src.models.agent_spec_enhanced import AgentSpecV2Enhanced, AgencyLevel
from src.services.config import Config
from src.services.variable_resolver import VariableResolver


class TestFlowConverter:
    """Test cases for FlowConverter class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "test-api-key"
        return config

    @pytest.fixture
    def mock_variable_resolver(self):
        """Create a mock variable resolver."""
        resolver = Mock(spec=VariableResolver)
        resolver.resolve.return_value = {}
        return resolver

    @pytest.fixture
    def flow_converter(self, mock_config, mock_variable_resolver):
        """Create a FlowConverter instance with mocked dependencies."""
        converter = FlowConverter(mock_config, mock_variable_resolver)
        return converter

    @pytest.fixture
    def sample_spec(self):
        """Create a sample agent specification."""
        return {
            "id": "test-agent",
            "name": "Test Agent",
            "agentGoal": "Test agent for unit testing",
            "components": [
                {
                    "id": "input",
                    "name": "Input",
                    "type": "genesis:chat_input",
                    "provides": [
                        {
                            "useAs": "input",
                            "in": "agent",
                            "description": "User input"
                        }
                    ]
                },
                {
                    "id": "agent",
                    "name": "Test Agent",
                    "type": "genesis:agent",
                    "config": {
                        "agent_llm": "Azure OpenAI",
                        "model_name": "gpt-4",
                        "temperature": 0.7
                    },
                    "provides": [
                        {
                            "useAs": "input",
                            "in": "output",
                            "description": "Agent response"
                        }
                    ]
                },
                {
                    "id": "output",
                    "name": "Output",
                    "type": "genesis:chat_output",
                    "config": {
                        "should_store_message": True
                    }
                }
            ]
        }

    @pytest.fixture
    def mock_component_data(self):
        """Create mock component data from Genesis Studio."""
        return {
            "agents": {
                "Agent": {
                    "template": {
                        "agent_llm": {
                            "name": "agent_llm",
                            "display_name": "Model Provider",
                            "value": "OpenAI",
                            "options": ["OpenAI", "Azure OpenAI", "Anthropic"],
                            "type": "str"
                        },
                        "model_name": {
                            "name": "model_name",
                            "display_name": "Model Name",
                            "value": "gpt-4",
                            "type": "str"
                        },
                        "temperature": {
                            "name": "temperature",
                            "display_name": "Temperature",
                            "value": 0.7,
                            "type": "float"
                        },
                        "system_prompt": {
                            "name": "system_prompt",
                            "display_name": "System Prompt",
                            "value": "",
                            "type": "str"
                        }
                    },
                    "outputs": [
                        {
                            "name": "response",
                            "types": ["Message"],
                            "display_name": "Response"
                        }
                    ]
                },
                "PromptTemplate": {
                    "template": {
                        "saved_prompt": {
                            "name": "saved_prompt",
                            "display_name": "Saved Prompt",
                            "value": "",
                            "type": "str"
                        },
                        "template": {
                            "name": "template",
                            "display_name": "Template",
                            "value": "",
                            "type": "str"
                        }
                    },
                    "outputs": [
                        {
                            "name": "prompt",
                            "types": ["Message", "str"],
                            "display_name": "Prompt"
                        }
                    ]
                }
            },
            "inputs": {
                "ChatInput": {
                    "template": {},
                    "outputs": [
                        {
                            "name": "message",
                            "types": ["Message"],
                            "display_name": "Message"
                        }
                    ]
                }
            },
            "outputs": {
                "ChatOutput": {
                    "template": {
                        "should_store_message": {
                            "name": "should_store_message",
                            "value": True,
                            "type": "bool"
                        },
                        "input_value": {
                            "name": "input_value",
                            "input_types": ["Message"],
                            "type": "str"
                        }
                    }
                }
            }
        }

    def test_flow_converter_initialization(self, mock_config, mock_variable_resolver):
        """Test FlowConverter initialization."""
        converter = FlowConverter(mock_config, mock_variable_resolver)
        assert converter.config == mock_config
        assert converter.variable_resolver == mock_variable_resolver
        assert converter.dynamic_mapper is None

    @pytest.mark.asyncio
    async def test_build_node_basic(self, flow_converter, mock_component_data):
        """Test building a basic node from component specification."""
        # Setup mock dynamic mapper
        flow_converter.dynamic_mapper = Mock()
        flow_converter.dynamic_mapper.get_component_type.return_value = "ChatInput"
        flow_converter.dynamic_mapper._components_cache = mock_component_data
        
        component = {
            "id": "input",
            "name": "User Input",
            "type": "genesis:chat_input",
            "description": "Receive user input"
        }
        
        node = await flow_converter._build_node(component, 0)
        
        assert node is not None
        assert node["id"] == "input"
        assert node["type"] == "genericNode"
        assert node["data"]["type"] == "ChatInput"
        assert node["data"]["display_name"] == "User Input"
        assert node["data"]["description"] == "Receive user input"

    @pytest.mark.asyncio
    async def test_build_node_with_config(self, flow_converter, mock_component_data):
        """Test building a node with configuration values."""
        # Setup mock dynamic mapper
        flow_converter.dynamic_mapper = Mock()
        flow_converter.dynamic_mapper.get_component_type.return_value = "Agent"
        flow_converter.dynamic_mapper._components_cache = mock_component_data
        
        component = {
            "id": "agent",
            "name": "Test Agent",
            "type": "genesis:agent",
            "config": {
                "agent_llm": "Azure OpenAI",
                "model_name": "gpt-4",
                "temperature": 0.5
            }
        }
        
        node = await flow_converter._build_node(component, 0)
        
        assert node is not None
        assert node["data"]["node"]["template"]["agent_llm"]["value"] == "Azure OpenAI"
        assert node["data"]["node"]["template"]["model_name"]["value"] == "gpt-4"
        assert node["data"]["node"]["template"]["temperature"]["value"] == 0.5

    @pytest.mark.asyncio
    async def test_build_node_as_tool(self, flow_converter, mock_component_data):
        """Test building a node that is used as a tool."""
        # Setup mock dynamic mapper
        flow_converter.dynamic_mapper = Mock()
        flow_converter.dynamic_mapper.get_component_type.return_value = "Agent"
        flow_converter.dynamic_mapper._components_cache = mock_component_data
        
        # Mock the _is_component_used_as_tool method
        flow_converter._is_component_used_as_tool = Mock(return_value=True)
        
        component = {
            "id": "tool-agent",
            "name": "Tool Agent",
            "type": "genesis:agent",
            "provides": [
                {
                    "useAs": "tools",
                    "in": "main-agent"
                }
            ]
        }
        
        node = await flow_converter._build_node(component, 0)
        
        assert node is not None
        assert node["data"]["node"]["tool_mode"] is True
        assert any(
            output.get("name") == "component_as_tool" 
            for output in node["data"]["node"]["outputs"]
        )

    def test_create_edge_from_provides(self, flow_converter):
        """Test creating an edge from provides declaration."""
        source_id = "input"
        provide = {
            "useAs": "input",
            "in": "agent",
            "description": "Connect input to agent"
        }
        
        node_map = {
            "input": {
                "id": "input",
                "data": {
                    "type": "ChatInput",
                    "outputs": [
                        {
                            "name": "message",
                            "types": ["Message"]
                        }
                    ]
                }
            },
            "agent": {
                "id": "agent",
                "data": {
                    "type": "Agent",
                    "node": {
                        "template": {
                            "input_value": {
                                "input_types": ["Message"]
                            }
                        }
                    }
                }
            }
        }
        
        edge = flow_converter._create_edge_from_provides(
            source_id, provide, node_map, {"type": "genesis:chat_input"}
        )
        
        assert edge is not None
        assert edge["source"] == "input"
        assert edge["target"] == "agent"
        assert edge["data"]["sourceHandle"]["name"] == "message"
        assert edge["data"]["targetHandle"]["fieldName"] == "input_value"

    def test_map_use_as_to_field(self, flow_converter):
        """Test mapping useAs values to field names."""
        mappings = {
            "input": "input_value",
            "tool": "tools",
            "tools": "tools",
            "system_prompt": "system_prompt",
            "prompt": "system_prompt",
            "llm": "llm",
            "response": "input_value",
            "message": "message",
            "text": "text",
            "output": "input_value"
        }
        
        for use_as, expected_field in mappings.items():
            assert flow_converter._map_use_as_to_field(use_as) == expected_field

    def test_determine_output_field(self, flow_converter):
        """Test determining output field based on useAs and component type."""
        # Test tool output
        node = {"data": {"outputs": []}}
        assert flow_converter._determine_output_field("tools", node, "Agent") == "component_as_tool"
        
        # Test agent response output
        node = {
            "data": {
                "outputs": [
                    {"name": "response", "types": ["Message"]}
                ]
            }
        }
        assert flow_converter._determine_output_field("response", node, "Agent") == "response"
        
        # Test prompt output
        node = {
            "data": {
                "outputs": [
                    {"name": "prompt", "types": ["Message", "str"]}
                ]
            }
        }
        assert flow_converter._determine_output_field("prompt", node, "PromptTemplate") == "prompt"

    def test_validate_type_compatibility(self, flow_converter):
        """Test type compatibility validation."""
        # Test compatible types
        assert flow_converter._validate_type_compatibility(
            ["Message"], ["Message"], "ChatInput", "Agent"
        ) is True
        
        # Test Tool compatibility
        assert flow_converter._validate_type_compatibility(
            ["Tool"], ["Tool"], "Agent", "Agent"
        ) is True
        
        # Test Message to str compatibility
        assert flow_converter._validate_type_compatibility(
            ["Message"], ["str", "Message"], "ChatInput", "Agent"
        ) is True
        
        # Test incompatible types
        assert flow_converter._validate_type_compatibility(
            ["Message"], ["Data"], "ChatInput", "JSONOutput"
        ) is False

    def test_calculate_position(self, flow_converter):
        """Test node position calculation."""
        # Test agent position
        pos = flow_converter._calculate_position(0, "agents")
        assert pos["x"] == 400
        assert pos["y"] == 200
        
        # Test input position
        pos = flow_converter._calculate_position(0, "inputs")
        assert pos["x"] == 50
        assert pos["y"] == 200
        
        # Test position with offset
        pos = flow_converter._calculate_position(5, "agents")
        assert pos["x"] == 600  # 400 + (5 % 4) * 200
        assert pos["y"] == 350  # 200 + (5 // 4) * 150

    def test_get_node_height(self, flow_converter):
        """Test getting node height based on category."""
        heights = {
            "agents": 500,
            "prompts": 300,
            "tools": 350,
            "models": 400,
            "llms": 600,
            "outputs": 250,
            "inputs": 250
        }
        
        for category, expected_height in heights.items():
            assert flow_converter._get_node_height(category) == expected_height
        
        # Test default height
        assert flow_converter._get_node_height("unknown") == 350

    def test_determine_handle_type(self, flow_converter):
        """Test determining handle type for connections."""
        # Test tools handle
        assert flow_converter._determine_handle_type("tools", ["Tool"]) == "other"
        
        # Test multiple input types
        assert flow_converter._determine_handle_type("input_value", ["Data", "Message"]) == "other"
        
        # Test Message type
        assert flow_converter._determine_handle_type("input_value", ["Message"]) == "str"
        
        # Test single type
        assert flow_converter._determine_handle_type("data", ["Data"]) == "Data"

    @pytest.mark.asyncio
    async def test_build_edges(self, flow_converter):
        """Test building edges from component provides declarations."""
        spec = {
            "components": [
                {
                    "id": "input",
                    "provides": [
                        {
                            "useAs": "input",
                            "in": "agent",
                            "description": "User input"
                        }
                    ]
                },
                {
                    "id": "agent",
                    "provides": [
                        {
                            "useAs": "input",
                            "in": "output",
                            "description": "Agent response"
                        }
                    ]
                }
            ]
        }
        
        nodes = [
            {
                "id": "input",
                "data": {
                    "type": "ChatInput",
                    "outputs": [{"name": "message", "types": ["Message"]}]
                }
            },
            {
                "id": "agent",
                "data": {
                    "type": "Agent",
                    "outputs": [{"name": "response", "types": ["Message"]}],
                    "node": {
                        "template": {
                            "input_value": {"input_types": ["Message"]}
                        }
                    }
                }
            },
            {
                "id": "output",
                "data": {
                    "type": "ChatOutput",
                    "node": {
                        "template": {
                            "input_value": {"input_types": ["Message"]}
                        }
                    }
                }
            }
        ]
        
        edges = await flow_converter._build_edges(spec, nodes)
        
        assert len(edges) == 2
        assert edges[0]["source"] == "input"
        assert edges[0]["target"] == "agent"
        assert edges[1]["source"] == "agent"
        assert edges[1]["target"] == "output"

    def test_apply_config_to_template(self, flow_converter):
        """Test applying configuration to node template."""
        template = {
            "temperature": {"value": 0.7, "type": "float"},
            "model_name": {"value": "gpt-3.5", "type": "str"},
            "max_tokens": {"value": 1000, "type": "int"}
        }
        
        config = {
            "temperature": 0.5,
            "model_name": "gpt-4",
            "max_tokens": 2000
        }
        
        flow_converter._apply_config_to_template(template, config)
        
        assert template["temperature"]["value"] == 0.5
        assert template["model_name"]["value"] == "gpt-4"
        assert template["max_tokens"]["value"] == 2000

    def test_apply_config_with_agent_goal(self, flow_converter):
        """Test applying agentGoal as system_prompt for Agent components."""
        template = {
            "system_prompt": {"value": "", "type": "str"}
        }
        
        config = {}
        component = {"type": "genesis:agent"}
        spec = Mock()
        spec.agentGoal = "This is the agent goal"
        
        flow_converter._apply_config_to_template(template, config, component, spec)
        
        assert template["system_prompt"]["value"] == "This is the agent goal"

    def test_filter_invalid_components(self, flow_converter):
        """Test filtering out invalid components."""
        spec = Mock()
        spec.components = [
            {"type": "genesis:valid_component"},
            {"type": "genesis:invalid_component"},
            {"type": "genesis:another_valid"}
        ]
        
        missing = ["genesis:invalid_component"]
        
        filtered_spec = flow_converter._filter_invalid_components(spec, missing)
        
        assert len(filtered_spec.components) == 2
        assert all(comp["type"] not in missing for comp in filtered_spec.components)

    def test_validate_flow(self, flow_converter):
        """Test flow validation."""
        # Valid flow
        valid_flow = {
            "data": {
                "nodes": [
                    {"id": "1", "type": "ChatInput", "data": {}},
                    {"id": "2", "type": "Agent", "data": {}}
                ],
                "edges": [
                    {
                        "source": "1",
                        "target": "2",
                        "sourceHandle": "handle1",
                        "targetHandle": "handle2"
                    }
                ]
            }
        }
        
        errors = flow_converter.validate_flow(valid_flow)
        assert len(errors) == 0
        
        # Invalid flow - missing data
        invalid_flow = {}
        errors = flow_converter.validate_flow(invalid_flow)
        assert "Missing 'data' field in flow" in errors
        
        # Invalid flow - missing nodes
        invalid_flow = {"data": {"edges": []}}
        errors = flow_converter.validate_flow(invalid_flow)
        assert "Missing 'nodes' in flow data" in errors
        
        # Invalid flow - node missing id
        invalid_flow = {
            "data": {
                "nodes": [{"type": "Agent", "data": {}}],
                "edges": []
            }
        }
        errors = flow_converter.validate_flow(invalid_flow)
        assert any("missing 'id'" in error for error in errors)

    @pytest.mark.asyncio
    async def test_convert_with_enhanced_spec(self, flow_converter, sample_spec):
        """Test converting an enhanced specification to flow."""
        # Mock dependencies
        flow_converter.parser.parse_specification = Mock(return_value=sample_spec)
        flow_converter.component_validator.validate_spec = AsyncMock(
            return_value={
                "valid": True,
                "errors": [],
                "warnings": [],
                "missing_components": []
            }
        )
        
        # Mock dynamic mapper
        flow_converter.dynamic_mapper = Mock()
        flow_converter.dynamic_mapper.get_component_type = Mock(side_effect=lambda x: {
            "genesis:chat_input": "ChatInput",
            "genesis:agent": "Agent",
            "genesis:chat_output": "ChatOutput"
        }.get(x, "Unknown"))
        
        # Mock component data
        flow_converter.dynamic_mapper._components_cache = {
            "inputs": {
                "ChatInput": {"template": {}, "outputs": [{"name": "message", "types": ["Message"]}]}
            },
            "agents": {
                "Agent": {
                    "template": {
                        "agent_llm": {"value": "OpenAI"},
                        "model_name": {"value": "gpt-4"},
                        "temperature": {"value": 0.7}
                    },
                    "outputs": [{"name": "response", "types": ["Message"]}]
                }
            },
            "outputs": {
                "ChatOutput": {
                    "template": {
                        "should_store_message": {"value": True},
                        "input_value": {"input_types": ["Message"]}
                    }
                }
            }
        }
        
        # Mock _build_nodes and _build_edges
        mock_nodes = [
            {"id": "input", "data": {"type": "ChatInput"}},
            {"id": "agent", "data": {"type": "Agent"}},
            {"id": "output", "data": {"type": "ChatOutput"}}
        ]
        mock_edges = [
            {"source": "input", "target": "agent"},
            {"source": "agent", "target": "output"}
        ]
        
        flow_converter._build_nodes = AsyncMock(return_value=mock_nodes)
        flow_converter._build_edges = AsyncMock(return_value=mock_edges)
        
        # Convert
        flow = await flow_converter.convert("test.yaml")
        
        # Verify
        assert flow is not None
        assert "data" in flow
        assert flow["data"]["nodes"] == mock_nodes
        assert flow["data"]["edges"] == mock_edges
        assert flow["name"] == "Test Agent"

    def test_convert_sync(self, flow_converter):
        """Test synchronous wrapper for convert method."""
        # Mock the async convert method
        async def mock_convert(spec_path):
            return {"data": {"nodes": [], "edges": []}}
        
        flow_converter.convert = mock_convert
        
        # Call sync version
        result = flow_converter.convert_sync("test.yaml")
        
        assert result is not None
        assert "data" in result

    def test_apply_tweaks(self, flow_converter):
        """Test applying tweaks to flow."""
        flow = {
            "data": {
                "nodes": [
                    {
                        "id": "agent",
                        "data": {
                            "node": {
                                "template": {
                                    "temperature": {"value": 0.7}
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        tweaks = {
            "agent": {
                "temperature": 0.5
            }
        }
        
        # Mock variable resolver
        flow_converter.variable_resolver.apply_tweaks = Mock(return_value=flow)
        
        result = flow_converter.apply_tweaks(flow, tweaks)
        
        flow_converter.variable_resolver.apply_tweaks.assert_called_once_with(flow, tweaks)

    def test_resolve_flow(self, flow_converter):
        """Test resolving variables in flow."""
        flow = {
            "data": {
                "nodes": [
                    {
                        "data": {
                            "node": {
                                "template": {
                                    "model_name": {"value": "{model}"}
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Mock variable resolver
        resolved_flow = {
            "data": {
                "nodes": [
                    {
                        "data": {
                            "node": {
                                "template": {
                                    "model_name": {"value": "gpt-4"}
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        flow_converter.variable_resolver.resolve_flow = Mock(return_value=resolved_flow)
        
        result = flow_converter.resolve_flow(flow)
        
        assert result == resolved_flow
        flow_converter.variable_resolver.resolve_flow.assert_called_once_with(flow)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])