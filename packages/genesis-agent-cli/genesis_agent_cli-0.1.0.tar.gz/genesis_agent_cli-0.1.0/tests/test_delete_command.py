"""
Unit tests for the Delete command.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner

from src.commands.delete import delete


class TestDeleteCommand:
    """Test cases for delete command."""

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

    def test_delete_with_confirmation(self, cli_runner, mock_config):
        """Test delete with user confirmation."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class, \
             patch('src.commands.delete.click.confirm', return_value=True) as mock_confirm:
            
            # Mock API service
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(return_value=True)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123'])
            
            assert result.exit_code == 0
            assert "successfully deleted" in result.output
            
            # Verify confirmation was requested
            mock_confirm.assert_called_once_with(
                "Are you sure you want to delete agent/flow 'agent-123'?",
                abort=True
            )
            
            # Verify API was called
            mock_api.delete_flow.assert_called_once_with('agent-123')

    def test_delete_with_force_flag(self, cli_runner, mock_config):
        """Test delete with force flag (no confirmation)."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class, \
             patch('src.commands.delete.click.confirm') as mock_confirm:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(return_value=True)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            assert result.exit_code == 0
            assert "successfully deleted" in result.output
            
            # Verify confirmation was NOT requested
            mock_confirm.assert_not_called()
            
            # Verify API was called
            mock_api.delete_flow.assert_called_once_with('agent-123')

    def test_delete_cancelled_by_user(self, cli_runner, mock_config):
        """Test delete cancelled by user."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class, \
             patch('src.commands.delete.click.confirm', return_value=False) as mock_confirm:
            
            mock_api = Mock()
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123'])
            
            # When user cancels, click.confirm with abort=True will exit with code 1
            assert result.exit_code == 1
            
            # Verify API was NOT called
            mock_api.delete_flow.assert_not_called()

    def test_delete_not_found(self, cli_runner, mock_config):
        """Test delete when agent/flow not found."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(side_effect=Exception("404 Not Found"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['nonexistent-agent', '-f'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "404 Not Found" in result.output

    def test_delete_api_error(self, cli_runner, mock_config):
        """Test handling of API errors during deletion."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(side_effect=Exception("API Error: 500 Internal Server Error"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "500 Internal Server Error" in result.output

    def test_delete_unauthorized(self, cli_runner, mock_config):
        """Test delete with unauthorized access."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(side_effect=Exception("401 Unauthorized"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "401 Unauthorized" in result.output

    def test_delete_connection_error(self, cli_runner, mock_config):
        """Test handling of connection errors."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(side_effect=ConnectionError("Failed to connect to server"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "Failed to connect" in result.output

    def test_delete_multiple_agents(self, cli_runner, mock_config):
        """Test deleting multiple agents (if supported)."""
        # This test assumes the delete command might support multiple IDs in the future
        # Currently it takes a single agent_id, but this tests the pattern
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(return_value=True)
            mock_api_class.return_value = mock_api
            
            # Try with single ID (current implementation)
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            assert result.exit_code == 0
            mock_api.delete_flow.assert_called_once_with('agent-123')

    def test_delete_empty_agent_id(self, cli_runner, mock_config):
        """Test delete with empty agent ID."""
        result = cli_runner.invoke(delete, [''])
        
        # Click should handle this as missing argument
        assert result.exit_code != 0

    def test_delete_no_agent_id(self, cli_runner, mock_config):
        """Test delete without providing agent ID."""
        result = cli_runner.invoke(delete, [])
        
        assert result.exit_code == 2
        assert "Missing argument" in result.output

    def test_delete_special_characters_in_id(self, cli_runner, mock_config):
        """Test delete with special characters in agent ID."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(return_value=True)
            mock_api_class.return_value = mock_api
            
            # Test with URL-safe special characters
            special_id = "agent-123_v2.0"
            result = cli_runner.invoke(delete, [special_id, '-f'])
            
            assert result.exit_code == 0
            mock_api.delete_flow.assert_called_once_with(special_id)

    def test_delete_with_whitespace(self, cli_runner, mock_config):
        """Test delete with whitespace in agent ID."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(return_value=True)
            mock_api_class.return_value = mock_api
            
            # Test with ID containing spaces (should be trimmed or handled)
            result = cli_runner.invoke(delete, [' agent-123 ', '-f'])
            
            assert result.exit_code == 0
            # The command should handle whitespace appropriately
            mock_api.delete_flow.assert_called_once()

    def test_delete_timeout_error(self, cli_runner, mock_config):
        """Test handling of timeout errors."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(side_effect=TimeoutError("Request timed out"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            assert result.exit_code == 1
            assert "Error" in result.output

    def test_delete_returns_false(self, cli_runner, mock_config):
        """Test when API returns False (deletion failed)."""
        with patch('src.commands.delete.Config', return_value=mock_config), \
             patch('src.commands.delete.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.delete_flow = AsyncMock(return_value=False)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(delete, ['agent-123', '-f'])
            
            # Should handle False return value gracefully
            assert result.exit_code == 1 or "failed" in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])