"""
Unit tests for the Genesis Studio API client.
"""

import pytest
import httpx
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.services.genesis_studio_api import GenesisStudioAPI, Flow, FlowCreate, FlowData
from src.services.config import Config


class TestGenesisStudioAPI:
    """Test cases for GenesisStudioAPI class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "test-api-key"
        return config

    @pytest.fixture
    def api_client(self, mock_config):
        """Create a GenesisStudioAPI instance."""
        return GenesisStudioAPI(mock_config)

    @pytest.fixture
    def sample_flow_data(self):
        """Create sample flow data."""
        flow_id = uuid4()
        return {
            "id": str(flow_id),
            "name": "Test Agent",
            "description": "A test agent",
            "data": {
                "nodes": [
                    {"id": "node1", "type": "ChatInput"},
                    {"id": "node2", "type": "Agent"}
                ],
                "edges": [
                    {"source": "node1", "target": "node2"}
                ],
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            },
            "endpoint_name": "test-agent",
            "is_component": False,
            "updated_at": "2024-01-15T10:30:00Z",
            "folder_id": str(uuid4()),
            "user_id": str(uuid4())
        }

    def test_api_client_initialization(self, mock_config):
        """Test API client initialization."""
        client = GenesisStudioAPI(mock_config)
        
        assert client.config == mock_config
        assert client.base_url == "http://test.example.com"
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["Authorization"] == "Bearer test-api-key"

    def test_api_client_initialization_with_bearer_prefix(self):
        """Test API client initialization with Bearer prefix in API key."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "Bearer sk-test-key"
        
        client = GenesisStudioAPI(config)
        
        # Should not add double Bearer
        assert client.headers["Authorization"] == "Bearer sk-test-key"

    def test_api_client_initialization_no_api_key(self):
        """Test API client initialization without API key."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = None
        
        client = GenesisStudioAPI(config)
        
        assert "Authorization" not in client.headers

    @pytest.mark.asyncio
    async def test_list_flows_success(self, api_client, sample_flow_data):
        """Test successful listing of flows."""
        flows_response = [sample_flow_data, {**sample_flow_data, "id": str(uuid4()), "name": "Another Agent"}]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = flows_response
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            flows = await api_client.list_flows()
            
            assert len(flows) == 2
            assert flows[0].name == "Test Agent"
            assert flows[1].name == "Another Agent"
            assert isinstance(flows[0], Flow)
            
            # Verify API call
            mock_async_client.get.assert_called_once_with(
                "http://test.example.com/api/v1/flows/",
                headers=api_client.headers
            )

    @pytest.mark.asyncio
    async def test_list_flows_empty(self, api_client):
        """Test listing flows when none exist."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            flows = await api_client.list_flows()
            
            assert len(flows) == 0

    @pytest.mark.asyncio
    async def test_list_flows_http_error(self, api_client):
        """Test handling of HTTP errors when listing flows."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=None, response=mock_response
            )
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await api_client.list_flows()

    @pytest.mark.asyncio
    async def test_get_flow_success(self, api_client, sample_flow_data):
        """Test successful retrieval of a single flow."""
        flow_id = sample_flow_data["id"]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_flow_data
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            flow = await api_client.get_flow(flow_id)
            
            assert flow.name == "Test Agent"
            assert str(flow.id) == flow_id
            assert flow.description == "A test agent"
            assert isinstance(flow, Flow)
            
            # Verify API call
            mock_async_client.get.assert_called_once_with(
                f"http://test.example.com/api/v1/flows/{flow_id}/",
                headers=api_client.headers
            )

    @pytest.mark.asyncio
    async def test_get_flow_not_found(self, api_client):
        """Test retrieving non-existent flow."""
        flow_id = str(uuid4())
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=None, response=mock_response
            )
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await api_client.get_flow(flow_id)

    @pytest.mark.asyncio
    async def test_create_flow_success(self, api_client, sample_flow_data):
        """Test successful flow creation."""
        flow_create = FlowCreate(
            name="New Agent",
            description="A new test agent",
            data={
                "nodes": [{"id": "input", "type": "ChatInput"}],
                "edges": [{"source": "input", "target": "output"}]
            }
        )
        
        with patch('httpx.AsyncClient') as mock_client, \
             patch('builtins.print'):  # Suppress debug prints
            
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                **sample_flow_data,
                "name": flow_create.name,
                "description": flow_create.description
            }
            
            mock_async_client = AsyncMock()
            mock_async_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            flow = await api_client.create_flow(flow_create)
            
            assert flow.name == "New Agent"
            assert flow.description == "A new test agent"
            
            # Verify API call
            mock_async_client.post.assert_called_once()
            call_args = mock_async_client.post.call_args
            assert call_args[0][0] == "http://test.example.com/api/v1/flows/"
            assert call_args[1]["json"]["name"] == "New Agent"
            assert "edges" in call_args[1]["json"]["data"]

    @pytest.mark.asyncio
    async def test_create_flow_with_edges_debug(self, api_client, sample_flow_data, capsys):
        """Test flow creation with edge debugging output."""
        flow_create = FlowCreate(
            name="Test Agent",
            data={
                "nodes": [],
                "edges": [
                    {"source": "a", "target": "b"},
                    {"source": "b", "target": "c"}
                ]
            }
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = sample_flow_data
            
            mock_async_client = AsyncMock()
            mock_async_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            await api_client.create_flow(flow_create)
            
            # Check debug output
            captured = capsys.readouterr()
            assert "Sending 2 edges in API request" in captured.out
            assert "Edge 1: a -> b" in captured.out
            assert "Edge 2: b -> c" in captured.out

    @pytest.mark.asyncio
    async def test_update_flow_success(self, api_client, sample_flow_data):
        """Test successful flow update."""
        flow_id = sample_flow_data["id"]
        update_data = {
            "name": "Updated Agent",
            "description": "Updated description"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                **sample_flow_data,
                **update_data
            }
            
            mock_async_client = AsyncMock()
            mock_async_client.patch.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            flow = await api_client.update_flow(flow_id, update_data)
            
            assert flow.name == "Updated Agent"
            assert flow.description == "Updated description"
            
            # Verify API call
            mock_async_client.patch.assert_called_once_with(
                f"http://test.example.com/api/v1/flows/{flow_id}/",
                headers=api_client.headers,
                json=update_data
            )

    @pytest.mark.asyncio
    async def test_delete_flow_success(self, api_client):
        """Test successful flow deletion."""
        flow_id = str(uuid4())
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 204
            
            mock_async_client = AsyncMock()
            mock_async_client.delete.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            # Should not raise exception
            await api_client.delete_flow(flow_id)
            
            # Verify API call
            mock_async_client.delete.assert_called_once_with(
                f"http://test.example.com/api/v1/flows/{flow_id}/",
                headers=api_client.headers
            )

    @pytest.mark.asyncio
    async def test_delete_flow_not_found(self, api_client):
        """Test deleting non-existent flow."""
        flow_id = str(uuid4())
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=None, response=mock_response
            )
            
            mock_async_client = AsyncMock()
            mock_async_client.delete.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await api_client.delete_flow(flow_id)

    @pytest.mark.asyncio
    async def test_check_health_success(self, api_client):
        """Test successful health check."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            is_healthy = await api_client.check_health()
            
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_check_health_failure(self, api_client):
        """Test health check failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 503
            
            mock_async_client = AsyncMock()
            mock_async_client.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            is_healthy = await api_client.check_health()
            
            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_check_health_exception(self, api_client):
        """Test health check with network exception."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_async_client.get.side_effect = httpx.NetworkError("Connection failed")
            mock_client.return_value.__aenter__.return_value = mock_async_client
            
            is_healthy = await api_client.check_health()
            
            assert is_healthy is False


class TestFlowModels:
    """Test cases for Flow-related models."""

    def test_flow_data_model(self):
        """Test FlowData model."""
        flow_data = FlowData(
            nodes=[{"id": "1", "type": "Agent"}],
            edges=[{"source": "1", "target": "2"}],
            viewport={"x": 100, "y": 200}
        )
        
        assert len(flow_data.nodes) == 1
        assert len(flow_data.edges) == 1
        assert flow_data.viewport["x"] == 100

    def test_flow_data_defaults(self):
        """Test FlowData with defaults."""
        flow_data = FlowData()
        
        assert flow_data.nodes == []
        assert flow_data.edges == []
        assert flow_data.viewport == {}

    def test_flow_model(self):
        """Test Flow model."""
        flow_id = uuid4()
        flow = Flow(
            id=flow_id,
            name="Test Flow",
            description="A test flow",
            data={"nodes": [], "edges": []},
            endpoint_name="test-flow",
            is_component=True,
            updated_at="2024-01-15T10:00:00Z",
            folder_id=uuid4(),
            user_id=uuid4()
        )
        
        assert flow.id == flow_id
        assert flow.name == "Test Flow"
        assert flow.is_component is True

    def test_flow_model_minimal(self):
        """Test Flow model with minimal fields."""
        flow = Flow(
            id=uuid4(),
            name="Minimal Flow"
        )
        
        assert flow.name == "Minimal Flow"
        assert flow.description is None
        assert flow.data is None
        assert flow.is_component is False

    def test_flow_create_model(self):
        """Test FlowCreate model."""
        flow_create = FlowCreate(
            name="New Flow",
            description="Description",
            data={"nodes": [], "edges": []},
            endpoint_name="new-flow",
            is_component=True
        )
        
        assert flow_create.name == "New Flow"
        assert flow_create.is_component is True
        
        # Test model_dump
        dumped = flow_create.model_dump(exclude_none=True)
        assert "name" in dumped
        assert "description" in dumped
        assert "data" in dumped

    def test_flow_create_minimal(self):
        """Test FlowCreate with minimal fields."""
        flow_create = FlowCreate(
            name="Minimal",
            data={}
        )
        
        assert flow_create.name == "Minimal"
        assert flow_create.description is None
        assert flow_create.is_component is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])