"""
Unit tests for the List command.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner
from datetime import datetime

from src.commands.list_agents import list_agents, display_agents_table, display_agents_detailed, display_agents_json


class TestListCommand:
    """Test cases for list command."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock()
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "test-api-key"
        return config

    @pytest.fixture
    def sample_flows(self):
        """Create sample flow data."""
        return [
            {
                "id": "flow-1",
                "name": "Test Agent 1",
                "description": "First test agent",
                "updated_at": "2024-01-15T10:30:00Z",
                "folder_id": "folder-1",
                "user_id": "user-1",
                "is_component": False
            },
            {
                "id": "flow-2",
                "name": "Test Agent 2",
                "description": "Second test agent",
                "updated_at": "2024-01-16T14:20:00Z",
                "folder_id": "folder-2",
                "user_id": "user-1",
                "is_component": True
            },
            {
                "id": "flow-3",
                "name": "Healthcare Workflow",
                "description": "Complex healthcare processing workflow",
                "updated_at": "2024-01-17T09:15:00Z",
                "folder_id": None,
                "user_id": "user-2",
                "is_component": False
            }
        ]

    def test_list_basic_success(self, cli_runner, mock_config, sample_flows):
        """Test basic list command success."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            # Mock API service
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=sample_flows)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents)
            
            assert result.exit_code == 0
            assert "Test Agent 1" in result.output
            assert "Test Agent 2" in result.output
            assert "Healthcare Workflow" in result.output
            
            # Verify API was called
            mock_api.list_flows.assert_called_once()

    def test_list_table_format(self, cli_runner, mock_config, sample_flows):
        """Test list with table format (default)."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=sample_flows)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents, ['-f', 'table'])
            
            assert result.exit_code == 0
            # Table format should have headers
            assert "ID" in result.output
            assert "Name" in result.output
            assert "Description" in result.output
            assert "Updated" in result.output
            assert "Type" in result.output

    def test_list_detailed_format(self, cli_runner, mock_config, sample_flows):
        """Test list with detailed format."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=sample_flows)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents, ['-f', 'detailed'])
            
            assert result.exit_code == 0
            # Detailed format should show more information
            assert "ID:" in result.output
            assert "Name:" in result.output
            assert "Description:" in result.output
            assert "Updated:" in result.output
            assert "Folder ID:" in result.output
            assert "User ID:" in result.output
            assert "Type:" in result.output

    def test_list_json_format(self, cli_runner, mock_config, sample_flows):
        """Test list with JSON format."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=sample_flows)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents, ['-f', 'json'])
            
            assert result.exit_code == 0
            
            # Should be valid JSON
            try:
                data = json.loads(result.output)
                assert len(data) == 3
                assert data[0]["id"] == "flow-1"
                assert data[1]["name"] == "Test Agent 2"
            except json.JSONDecodeError:
                pytest.fail("Output is not valid JSON")

    def test_list_with_limit(self, cli_runner, mock_config, sample_flows):
        """Test list with limit parameter."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            # Return only 2 flows when limit is applied
            limited_flows = sample_flows[:2]
            mock_api.list_flows = AsyncMock(return_value=limited_flows)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents, ['-l', '2'])
            
            assert result.exit_code == 0
            assert "Test Agent 1" in result.output
            assert "Test Agent 2" in result.output
            assert "Healthcare Workflow" not in result.output

    def test_list_no_flows(self, cli_runner, mock_config):
        """Test list when no flows exist."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=[])
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents)
            
            assert result.exit_code == 0
            assert "No agents/flows found" in result.output

    def test_list_api_error(self, cli_runner, mock_config):
        """Test handling of API errors."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(side_effect=Exception("API Error: 401 Unauthorized"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents)
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "401 Unauthorized" in result.output

    def test_display_agents_table(self, sample_flows):
        """Test table display function."""
        # Capture print output
        with patch('builtins.print') as mock_print:
            display_agents_table(sample_flows)
            
            # Check that print was called
            assert mock_print.called
            
            # Get all printed lines
            printed_lines = [str(call[0][0]) for call in mock_print.call_args_list]
            full_output = '\n'.join(printed_lines)
            
            # Verify table contents
            assert "flow-1" in full_output
            assert "Test Agent 1" in full_output
            assert "Component" in full_output  # Type column
            assert "Flow" in full_output       # Type column

    def test_display_agents_detailed(self, sample_flows):
        """Test detailed display function."""
        with patch('builtins.print') as mock_print:
            display_agents_detailed(sample_flows)
            
            # Get all printed lines
            printed_lines = [str(call[0][0]) for call in mock_print.call_args_list if call[0]]
            full_output = '\n'.join(printed_lines)
            
            # Verify detailed output
            assert "ID: flow-1" in full_output
            assert "Name: Test Agent 1" in full_output
            assert "Description: First test agent" in full_output
            assert "Folder ID: folder-1" in full_output
            assert "User ID: user-1" in full_output
            assert "Type: Flow" in full_output
            
            # Check separators between entries
            separator_count = sum(1 for line in printed_lines if "─" in line)
            assert separator_count >= 2  # At least 2 separators for 3 flows

    def test_display_agents_json(self, sample_flows):
        """Test JSON display function."""
        with patch('builtins.print') as mock_print:
            display_agents_json(sample_flows)
            
            # Get the printed JSON
            json_output = mock_print.call_args[0][0]
            
            # Verify it's valid JSON
            data = json.loads(json_output)
            assert len(data) == 3
            assert all(flow in data for flow in sample_flows)

    def test_list_invalid_format(self, cli_runner, mock_config):
        """Test list with invalid format option."""
        with patch('src.commands.list_agents.Config', return_value=mock_config):
            result = cli_runner.invoke(list_agents, ['-f', 'invalid'])
            
            assert result.exit_code == 2
            assert "Invalid value" in result.output

    def test_list_negative_limit(self, cli_runner, mock_config):
        """Test list with negative limit."""
        with patch('src.commands.list_agents.Config', return_value=mock_config):
            result = cli_runner.invoke(list_agents, ['-l', '-5'])
            
            # Click should validate this
            assert result.exit_code == 2

    def test_list_handles_missing_fields(self, cli_runner, mock_config):
        """Test list handles flows with missing optional fields."""
        incomplete_flows = [
            {
                "id": "flow-1",
                "name": "Test Agent",
                # Missing description, updated_at, folder_id, etc.
            }
        ]
        
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=incomplete_flows)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents)
            
            assert result.exit_code == 0
            assert "flow-1" in result.output
            assert "Test Agent" in result.output

    def test_list_formats_dates_correctly(self, cli_runner, mock_config):
        """Test that dates are formatted correctly in output."""
        flows_with_dates = [
            {
                "id": "flow-1",
                "name": "Test Agent",
                "updated_at": "2024-01-15T10:30:00Z",
                "description": "Test"
            }
        ]
        
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=flows_with_dates)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents, ['-f', 'table'])
            
            assert result.exit_code == 0
            # Date should be formatted nicely, not as ISO string
            assert "2024-01-15" in result.output or "Jan 15" in result.output

    def test_list_truncates_long_descriptions(self, cli_runner, mock_config):
        """Test that long descriptions are truncated in table view."""
        flows_with_long_desc = [
            {
                "id": "flow-1",
                "name": "Test Agent",
                "description": "This is a very long description " * 10,  # 300+ chars
                "updated_at": "2024-01-15T10:30:00Z"
            }
        ]
        
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=flows_with_long_desc)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents, ['-f', 'table'])
            
            assert result.exit_code == 0
            # Should truncate with ellipsis
            assert "..." in result.output

    def test_list_connection_error(self, cli_runner, mock_config):
        """Test handling of connection errors."""
        with patch('src.commands.list_agents.Config', return_value=mock_config), \
             patch('src.commands.list_agents.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(side_effect=ConnectionError("Failed to connect"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(list_agents)
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "Failed to connect" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])