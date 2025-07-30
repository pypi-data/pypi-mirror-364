"""
Unit tests for the Component Loader service.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import httpx

from src.services.component_loader import ComponentLoader, ComponentValidator
from src.services.config import Config


class TestComponentLoader:
    """Test cases for ComponentLoader class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "test-api-key"
        return config

    @pytest.fixture
    def component_loader(self, mock_config):
        """Create a ComponentLoader instance."""
        return ComponentLoader(mock_config)

    @pytest.fixture
    def sample_components_response(self):
        """Create sample components API response."""
        return {
            "agents": {
                "Agent": {
                    "type": "Agent",
                    "display_name": "Agent",
                    "category": "agents",
                    "description": "Langflow Agent"
                },
                "AutonomizeAgent": {
                    "type": "AutonomizeAgent",
                    "display_name": "Autonomize Agent",
                    "category": "agents",
                    "description": "Enhanced agent"
                }
            },
            "llms": {
                "OpenAIModel": {
                    "type": "OpenAIModel",
                    "display_name": "OpenAI",
                    "category": "llms"
                },
                "AzureOpenAIModel": {
                    "type": "AzureOpenAIModel",
                    "display_name": "Azure OpenAI",
                    "category": "llms"
                }
            },
            "inputs": {
                "ChatInput": {
                    "type": "ChatInput",
                    "display_name": "Chat Input",
                    "category": "inputs"
                }
            }
        }

    @pytest.mark.asyncio
    async def test_load_components_with_dynamic_mapper(self, component_loader, sample_components_response):
        """Test loading components using dynamic mapper."""
        # Mock dynamic mapper
        mock_mapper = Mock()
        mock_mapper._components_cache = sample_components_response
        
        with patch('src.services.component_loader.get_dynamic_mapper', new_callable=AsyncMock) as mock_get_mapper:
            mock_get_mapper.return_value = mock_mapper
            
            components = await component_loader.load_components()
            
            assert len(components) == 5
            assert "Agent" in components
            assert "AutonomizeAgent" in components
            assert "OpenAIModel" in components
            assert "AzureOpenAIModel" in components
            assert "ChatInput" in components
            
            # Verify cache timestamp was set
            assert component_loader._cache_timestamp is not None

    @pytest.mark.asyncio
    async def test_load_components_from_api(self, component_loader, sample_components_response):
        """Test loading components from API when dynamic mapper fails."""
        # Mock failed dynamic mapper
        with patch('src.services.component_loader.get_dynamic_mapper', side_effect=Exception("Mapper error")), \
             patch('httpx.AsyncClient') as mock_client:
            
            # Mock API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_components_response
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await component_loader.load_components(use_dynamic_mapper=False)
            
            assert len(components) == 5
            assert "Agent" in components
            assert "OpenAIModel" in components

    @pytest.mark.asyncio
    async def test_load_components_cache_valid(self, component_loader):
        """Test that valid cache is used without API call."""
        # Pre-populate cache
        component_loader._component_cache = {"TestComponent": {"type": "TestComponent"}}
        component_loader._cache_timestamp = datetime.now()
        
        with patch('src.services.component_loader.get_dynamic_mapper') as mock_mapper:
            components = await component_loader.load_components()
            
            # Should not have called mapper due to valid cache
            mock_mapper.assert_not_called()
            assert components == {"TestComponent": {"type": "TestComponent"}}

    @pytest.mark.asyncio
    async def test_load_components_cache_expired(self, component_loader):
        """Test that expired cache triggers reload."""
        # Pre-populate expired cache
        component_loader._component_cache = {"OldComponent": {"type": "OldComponent"}}
        component_loader._cache_timestamp = datetime.now() - timedelta(hours=1)
        
        # Mock dynamic mapper
        mock_mapper = Mock()
        mock_mapper._components_cache = {"agents": {"NewComponent": {"type": "NewComponent"}}}
        
        with patch('src.services.component_loader.get_dynamic_mapper', new_callable=AsyncMock) as mock_get_mapper:
            mock_get_mapper.return_value = mock_mapper
            
            components = await component_loader.load_components()
            
            # Should have called mapper due to expired cache
            mock_get_mapper.assert_called_once()
            assert "NewComponent" in components
            assert "OldComponent" not in components

    @pytest.mark.asyncio
    async def test_load_components_force_refresh(self, component_loader):
        """Test force refresh ignores cache."""
        # Pre-populate valid cache
        component_loader._component_cache = {"CachedComponent": {"type": "CachedComponent"}}
        component_loader._cache_timestamp = datetime.now()
        
        # Mock dynamic mapper
        mock_mapper = Mock()
        mock_mapper._components_cache = {"agents": {"FreshComponent": {"type": "FreshComponent"}}}
        
        with patch('src.services.component_loader.get_dynamic_mapper', new_callable=AsyncMock) as mock_get_mapper:
            mock_get_mapper.return_value = mock_mapper
            
            components = await component_loader.load_components(force_refresh=True)
            
            # Should have called mapper despite valid cache
            mock_get_mapper.assert_called_once()
            assert "FreshComponent" in components
            assert "CachedComponent" not in components

    @pytest.mark.asyncio
    async def test_load_components_api_404_fallback(self, component_loader):
        """Test fallback to alternative endpoint on 404."""
        with patch('src.services.component_loader.get_dynamic_mapper', side_effect=Exception("Mapper error")), \
             patch('httpx.AsyncClient') as mock_client:
            
            # Mock 404 on first endpoint, success on second
            mock_response_404 = Mock()
            mock_response_404.status_code = 404
            
            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = {"agents": [{"type": "Agent"}]}
            
            mock_async_client = AsyncMock()
            mock_async_client.get.side_effect = [mock_response_404, mock_response_success]
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await component_loader.load_components(use_dynamic_mapper=False)
            
            # Should have made 2 calls
            assert mock_async_client.get.call_count == 2
            assert "Agent" in components

    @pytest.mark.asyncio
    async def test_load_components_api_failure_uses_defaults(self, component_loader):
        """Test that API failure loads default components."""
        with patch('src.services.component_loader.get_dynamic_mapper', side_effect=Exception("Mapper error")), \
             patch('httpx.AsyncClient') as mock_client:
            
            # Mock API failure
            mock_async_client = AsyncMock()
            mock_async_client.get.side_effect = httpx.HTTPError("Connection failed")
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await component_loader.load_components(use_dynamic_mapper=False)
            
            # Should have default components
            assert len(components) > 0
            assert "Agent" in components
            assert "ChatInput" in components
            assert "ChatOutput" in components
            assert "PromptTemplate" in components

    @pytest.mark.asyncio
    async def test_load_components_list_response_format(self, component_loader):
        """Test handling list format API response."""
        list_response = [
            {"type": "Component1", "display_name": "Component 1"},
            {"type": "Component2", "display_name": "Component 2"}
        ]
        
        with patch('src.services.component_loader.get_dynamic_mapper', side_effect=Exception("Mapper error")), \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = list_response
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await component_loader.load_components(use_dynamic_mapper=False)
            
            assert "Component1" in components
            assert "Component2" in components

    def test_validate_component(self, component_loader):
        """Test component validation."""
        component_loader._component_cache = {
            "Agent": {"type": "Agent"},
            "ChatInput": {"type": "ChatInput"}
        }
        
        # Test direct component
        assert component_loader.validate_component("Agent") is True
        assert component_loader.validate_component("ChatInput") is True
        assert component_loader.validate_component("Unknown") is False
        
        # Test with genesis: prefix
        with patch('src.services.component_loader.get_langflow_component_type') as mock_mapper:
            mock_mapper.return_value = "Agent"
            assert component_loader.validate_component("genesis:agent") is True

    def test_get_component_info(self, component_loader):
        """Test getting component information."""
        component_data = {
            "type": "Agent",
            "display_name": "Agent",
            "category": "agents"
        }
        component_loader._component_cache = {"Agent": component_data}
        
        # Test direct access
        info = component_loader.get_component_info("Agent")
        assert info == component_data
        
        # Test missing component
        info = component_loader.get_component_info("Unknown")
        assert info is None
        
        # Test with genesis: prefix
        with patch('src.services.component_loader.get_langflow_component_type') as mock_mapper:
            mock_mapper.return_value = "Agent"
            info = component_loader.get_component_info("genesis:agent")
            assert info == component_data

    def test_get_available_components(self, component_loader):
        """Test getting list of available components."""
        component_loader._component_cache = {
            "Component1": {},
            "Component2": {},
            "Component3": {}
        }
        
        available = component_loader.get_available_components()
        assert len(available) == 3
        assert "Component1" in available
        assert "Component2" in available
        assert "Component3" in available

    def test_get_components_by_category(self, component_loader):
        """Test getting components by category."""
        component_loader._component_cache = {
            "Agent1": {"category": "agents"},
            "Agent2": {"category": "agents"},
            "Tool1": {"category": "tools"},
            "Input1": {"category": "inputs"}
        }
        
        agents = component_loader.get_components_by_category("agents")
        assert len(agents) == 2
        
        tools = component_loader.get_components_by_category("tools")
        assert len(tools) == 1
        
        unknown = component_loader.get_components_by_category("unknown")
        assert len(unknown) == 0

    def test_load_default_components(self, component_loader):
        """Test loading default components."""
        component_loader._load_default_components()
        
        assert len(component_loader._component_cache) > 0
        assert "Agent" in component_loader._component_cache
        assert "ChatInput" in component_loader._component_cache
        assert "ChatOutput" in component_loader._component_cache
        assert "PromptTemplate" in component_loader._component_cache
        assert "OpenAIModel" in component_loader._component_cache
        assert "AzureOpenAIModel" in component_loader._component_cache


class TestComponentValidator:
    """Test cases for ComponentValidator class."""

    @pytest.fixture
    def mock_loader(self):
        """Create a mock component loader."""
        loader = Mock(spec=ComponentLoader)
        loader.load_components = AsyncMock(return_value={})
        loader.validate_component = Mock(return_value=True)
        loader.get_available_components = Mock(return_value=["Agent", "ChatInput", "ChatOutput"])
        return loader

    @pytest.fixture
    def validator(self, mock_loader):
        """Create a ComponentValidator instance."""
        return ComponentValidator(mock_loader)

    @pytest.mark.asyncio
    async def test_validate_spec_all_valid(self, validator, mock_loader):
        """Test validating spec with all valid components."""
        spec = Mock()
        spec.components = [
            Mock(type="genesis:agent"),
            Mock(type="genesis:chat_input"),
            Mock(type="genesis:chat_output")
        ]
        
        mock_loader.validate_component.return_value = True
        
        result = await validator.validate_spec(spec)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert len(result["missing_components"]) == 0
        assert len(result["available_components"]) == 3

    @pytest.mark.asyncio
    async def test_validate_spec_missing_component(self, validator, mock_loader):
        """Test validating spec with missing component."""
        spec = Mock()
        spec.components = [
            Mock(type="genesis:agent"),
            Mock(type="genesis:unknown_component")
        ]
        
        mock_loader.validate_component.side_effect = lambda x: x != "genesis:unknown_component"
        
        result = await validator.validate_spec(spec)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "genesis:unknown_component" in result["missing_components"]
        assert len(result["available_components"]) == 1

    @pytest.mark.asyncio
    async def test_validate_spec_with_similar_suggestions(self, validator, mock_loader):
        """Test validation provides similar component suggestions."""
        spec = Mock()
        spec.components = [Mock(type="genesis:chatinput")]  # Missing underscore
        
        mock_loader.validate_component.return_value = False
        mock_loader.get_available_components.return_value = ["ChatInput", "ChatOutput", "TextInput"]
        
        with patch.object(validator, '_find_similar_components', return_value=["ChatInput"]):
            result = await validator.validate_spec(spec)
            
            assert result["valid"] is False
            assert len(result["warnings"]) == 1
            assert "Similar: ChatInput" in result["warnings"][0]

    @pytest.mark.asyncio
    async def test_validate_dict_spec(self, validator, mock_loader):
        """Test validating dictionary format spec."""
        spec = {
            "agent": {"type": "genesis:agent"},
            "tools": [
                {"type": "genesis:calculator"},
                {"type": "genesis:search"}
            ],
            "outputs": [
                {"type": "genesis:chat_output"}
            ]
        }
        
        mock_loader.validate_component.return_value = True
        
        result = await validator.validate_spec(spec)
        
        # Should have validated 4 components
        assert mock_loader.validate_component.call_count == 4

    def test_extract_component_types_from_object(self, validator):
        """Test extracting component types from object spec."""
        spec = Mock()
        spec.components = [
            Mock(type="type1"),
            Mock(type="type2"),
            Mock(type="type3")
        ]
        
        types = validator._extract_component_types(spec)
        
        assert len(types) == 3
        assert "type1" in types
        assert "type2" in types
        assert "type3" in types

    def test_extract_component_types_from_dict(self, validator):
        """Test extracting component types from dict spec."""
        spec = {
            "agent": {"type": "agent_type"},
            "tools": [
                {"type": "tool1"},
                {"type": "tool2"}
            ],
            "outputs": [
                {"type": "output1"}
            ]
        }
        
        types = validator._extract_component_types(spec)
        
        assert len(types) == 4
        assert "agent_type" in types
        assert "tool1" in types
        assert "tool2" in types
        assert "output1" in types

    def test_find_similar_components(self, validator, mock_loader):
        """Test finding similar components."""
        mock_loader.get_available_components.return_value = [
            "ChatInput", "ChatOutput", "TextInput", 
            "Agent", "AutonomizeAgent", "Tool"
        ]
        
        # Test similar to "chat"
        similar = validator._find_similar_components("genesis:chat")
        assert "ChatInput" in similar
        assert "ChatOutput" in similar
        
        # Test similar to "agent"
        similar = validator._find_similar_components("agent_component")
        assert "Agent" in similar or "AutonomizeAgent" in similar
        
        # Test max 3 results
        similar = validator._find_similar_components("input")
        assert len(similar) <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])