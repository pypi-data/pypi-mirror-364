"""
Unit tests for the Dynamic Component Mapper module.
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import httpx

from src.registry.dynamic_component_mapper import (
    DynamicComponentMapper,
    get_dynamic_mapper,
    get_langflow_component_type
)
from src.services.config import Config


class TestDynamicComponentMapper:
    """Test cases for DynamicComponentMapper class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "test-api-key"
        return config

    @pytest.fixture
    def mapper(self, mock_config):
        """Create a DynamicComponentMapper instance."""
        return DynamicComponentMapper(mock_config)

    @pytest.fixture
    def sample_components_data(self):
        """Create sample components data."""
        return {
            "agents": {
                "AutonomizeAgent": {
                    "display_name": "Autonomize Agent",
                    "template": {},
                    "outputs": []
                },
                "Agent": {
                    "display_name": "Agent",
                    "template": {},
                    "outputs": []
                }
            },
            "autonomize_models": {
                "RxNorm": {
                    "display_name": "RxNorm Code",
                    "template": {},
                    "outputs": []
                },
                "ICD10": {
                    "display_name": "ICD-10 Code",
                    "template": {},
                    "outputs": []
                }
            },
            "inputs": {
                "ChatInput": {
                    "display_name": "Chat Input",
                    "template": {},
                    "outputs": []
                }
            },
            "outputs": {
                "ChatOutput": {
                    "display_name": "Chat Output",
                    "template": {},
                    "outputs": []
                }
            },
            "prompts": {
                "PromptTemplate": {
                    "display_name": "Prompt Template",
                    "template": {},
                    "outputs": []
                }
            }
        }

    def test_mapper_initialization(self, mock_config):
        """Test DynamicComponentMapper initialization."""
        mapper = DynamicComponentMapper(mock_config)
        
        assert mapper.config == mock_config
        assert mapper._components_cache == {}
        assert mapper._component_map == {}
        assert mapper._cache_timestamp is None
        assert mapper._cache_duration == timedelta(hours=1)
        assert mapper._cache_file == "genesis_components_cache.json"

    def test_get_all_components(self, mapper, sample_components_data):
        """Test extracting all components from categorized structure."""
        mapper._components_cache = sample_components_data
        
        all_components = mapper._get_all_components()
        
        assert len(all_components) == 7
        assert "AutonomizeAgent" in all_components
        assert "Agent" in all_components
        assert "RxNorm" in all_components
        assert "ChatInput" in all_components
        assert "ChatOutput" in all_components
        assert "PromptTemplate" in all_components

    def test_build_component_map(self, mapper, sample_components_data):
        """Test building component map from cache."""
        mapper._components_cache = sample_components_data
        mapper._build_component_map()
        
        # Check basic mappings
        assert mapper._component_map["autonomizeagent"] == "AutonomizeAgent"
        assert mapper._component_map["agent"] == "Agent"
        assert mapper._component_map["rxnorm"] == "RxNorm"
        assert mapper._component_map["chatinput"] == "ChatInput"
        
        # Check display name mappings
        assert mapper._component_map["autonomize_agent"] == "AutonomizeAgent"
        assert mapper._component_map["autonomizeagent"] == "AutonomizeAgent"
        assert mapper._component_map["chat_input"] == "ChatInput"
        assert mapper._component_map["chatinput"] == "ChatInput"

    def test_get_component_type_with_genesis_prefix(self, mapper):
        """Test getting component type with genesis: prefix."""
        # Test direct mapping
        mapper._component_map = {
            "autonomize_agent": "AutonomizeAgent",
            "chat_input": "ChatInput"
        }
        
        assert mapper.get_component_type("genesis:autonomize_agent") == "AutonomizeAgent"
        assert mapper.get_component_type("genesis:chat_input") == "ChatInput"

    def test_get_component_type_without_prefix(self, mapper):
        """Test getting component type without genesis: prefix."""
        mapper._component_map = {
            "agent": "Agent"
        }
        
        assert mapper.get_component_type("agent") == "Agent"

    def test_get_component_type_with_intelligent_mapping(self, mapper):
        """Test intelligent mapping for unknown components."""
        # Empty component map to test fallback rules
        mapper._component_map = {}
        
        # Test specific mappings
        assert mapper.get_component_type("genesis:autonomize_agent") == "AutonomizeAgent"
        assert mapper.get_component_type("genesis:rxnorm") == "RxNorm"
        assert mapper.get_component_type("genesis:chat_input") == "ChatInput"
        assert mapper.get_component_type("genesis:chat_output") == "ChatOutput"
        assert mapper.get_component_type("genesis:prompt_template") == "PromptTemplate"
        assert mapper.get_component_type("genesis:conversation_memory") == "Memory"
        
        # Test pattern-based fallbacks
        assert mapper.get_component_type("genesis:some_agent") == "AutonomizeAgent"
        assert mapper.get_component_type("genesis:some_tool") == "CustomComponent"
        assert mapper.get_component_type("genesis:some_component") == "CustomComponent"
        assert mapper.get_component_type("genesis:some_memory") == "Memory"
        assert mapper.get_component_type("genesis:some_prompt") == "Prompt"
        assert mapper.get_component_type("genesis:some_input") == "ChatInput"
        assert mapper.get_component_type("genesis:some_output") == "ChatOutput"
        
        # Test clinical models
        assert mapper.get_component_type("genesis:clinical_llm") == "CustomComponent"
        assert mapper.get_component_type("genesis:provider_llm") == "AzureOpenAIModel"

    def test_validate_component(self, mapper, sample_components_data):
        """Test component validation."""
        mapper._components_cache = sample_components_data
        mapper._build_component_map()
        
        # Valid components
        assert mapper.validate_component("genesis:autonomize_agent") is True
        assert mapper.validate_component("genesis:chat_input") is True
        
        # Invalid component (but has intelligent mapping)
        assert mapper.validate_component("genesis:unknown_component") is False

    def test_get_available_components(self, mapper, sample_components_data):
        """Test getting available components."""
        mapper._components_cache = sample_components_data
        
        available = mapper.get_available_components()
        
        assert len(available) == 7
        assert "AutonomizeAgent" in available
        assert "ChatInput" in available

    @pytest.mark.asyncio
    async def test_load_components_from_cache_file(self, mapper, sample_components_data):
        """Test loading components from cache file."""
        # Create a temporary cache file
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "components": sample_components_data
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(cache_data, f)
            mapper._cache_file = f.name
            
            try:
                components = await mapper.load_components()
                
                assert components == sample_components_data
                assert mapper._components_cache == sample_components_data
                assert len(mapper._component_map) > 0
                
            finally:
                os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_load_components_from_expired_cache(self, mapper, sample_components_data):
        """Test loading components from expired cache file."""
        # Create an expired cache file
        old_timestamp = datetime.now() - timedelta(hours=2)
        cache_data = {
            "timestamp": old_timestamp.isoformat(),
            "components": sample_components_data
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(cache_data, f)
            mapper._cache_file = f.name
            
            # Mock the API call
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_components_data
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_async_client = AsyncMock()
                mock_async_client.get.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_async_client
                
                try:
                    components = await mapper.load_components()
                    
                    # Should have called the API due to expired cache
                    mock_async_client.get.assert_called_once()
                    assert components == sample_components_data
                    
                finally:
                    os.unlink(f.name)

    @pytest.mark.asyncio
    async def test_load_components_from_api(self, mapper, sample_components_data):
        """Test loading components from API."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_components_data
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await mapper.load_components(force_refresh=True)
            
            # Should have called the API
            mock_async_client.get.assert_called_once()
            expected_url = f"{mapper.config.genesis_studio_url}/api/v1/all?force_refresh=true"
            mock_async_client.get.assert_called_with(
                expected_url,
                headers={
                    "accept": "application/json",
                    "Authorization": f"Bearer {mapper.config.api_key}"
                }
            )
            
            assert components == sample_components_data
            assert mapper._components_cache == sample_components_data

    @pytest.mark.asyncio
    async def test_load_components_api_failure(self, mapper):
        """Test handling API failure when loading components."""
        # Mock API failure
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await mapper.load_components(force_refresh=True)
            
            # Should use fallback components
            assert "agents" in mapper._components_cache
            assert "AutonomizeAgent" in mapper._components_cache["agents"]

    @pytest.mark.asyncio
    async def test_load_components_network_error(self, mapper):
        """Test handling network error when loading components."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_async_client.get.side_effect = httpx.NetworkError("Connection failed")
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            components = await mapper.load_components(force_refresh=True)
            
            # Should use fallback components
            assert "agents" in mapper._components_cache
            assert len(mapper._component_map) > 0

    def test_is_cache_valid(self, mapper):
        """Test cache validity check."""
        # No cache timestamp
        assert mapper._is_cache_valid() is False
        
        # Recent cache
        mapper._cache_timestamp = datetime.now()
        mapper._components_cache = {"test": "data"}
        assert mapper._is_cache_valid() is True
        
        # Expired cache
        mapper._cache_timestamp = datetime.now() - timedelta(hours=2)
        assert mapper._is_cache_valid() is False
        
        # Empty cache
        mapper._cache_timestamp = datetime.now()
        mapper._components_cache = {}
        assert mapper._is_cache_valid() is False

    def test_load_fallback_components(self, mapper):
        """Test loading fallback components."""
        mapper._load_fallback_components()
        
        assert "agents" in mapper._components_cache
        assert "autonomize_models" in mapper._components_cache
        assert "inputs" in mapper._components_cache
        assert "outputs" in mapper._components_cache
        assert "prompts" in mapper._components_cache
        
        # Check some specific components
        assert "AutonomizeAgent" in mapper._components_cache["agents"]
        assert "ChatInput" in mapper._components_cache["inputs"]
        assert "ChatOutput" in mapper._components_cache["outputs"]

    @pytest.mark.asyncio
    async def test_load_components_with_auth_header_formatting(self, mapper):
        """Test auth header formatting when loading components."""
        # Test with Bearer prefix already present
        mapper.config.api_key = "Bearer test-key"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            await mapper.load_components(force_refresh=True)
            
            # Check that Bearer wasn't duplicated
            call_args = mock_async_client.get.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
        
        # Test without Bearer prefix
        mapper.config.api_key = "test-key"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            await mapper.load_components(force_refresh=True)
            
            # Check that Bearer was added
            call_args = mock_async_client.get.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"

    def test_get_langflow_component_type_function(self):
        """Test the standalone get_langflow_component_type function."""
        # Test with no cached mapper
        assert get_langflow_component_type("genesis:autonomize_agent") == "AutonomizeAgent"
        assert get_langflow_component_type("genesis:chat_input") == "ChatInput"
        assert get_langflow_component_type("genesis:unknown_agent") == "AutonomizeAgent"
        assert get_langflow_component_type("genesis:unknown_tool") == "CustomComponent"

    @pytest.mark.asyncio
    async def test_get_dynamic_mapper_singleton(self, mock_config):
        """Test that get_dynamic_mapper returns singleton instance."""
        # Mock load_components to avoid actual API calls
        with patch.object(DynamicComponentMapper, 'load_components', new_callable=AsyncMock):
            mapper1 = await get_dynamic_mapper(mock_config)
            mapper2 = await get_dynamic_mapper(mock_config)
            
            # Should be the same instance
            assert mapper1 is mapper2

    def test_component_type_normalization(self, mapper):
        """Test component type normalization with various formats."""
        mapper._component_map = {
            "test_component": "TestComponent"
        }
        
        # Test hyphen to underscore conversion
        assert mapper.get_component_type("genesis:test-component") == "TestComponent"
        
        # Test case insensitivity
        assert mapper.get_component_type("genesis:TEST_COMPONENT") == "TestComponent"
        assert mapper.get_component_type("genesis:Test_Component") == "TestComponent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])