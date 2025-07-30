"""
Unit tests for the Run command.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, mock_open
from click.testing import CliRunner

from src.commands.run import run, _deep_merge, _display_result


class TestRunCommand:
    """Test cases for run command."""

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
    def sample_flow(self):
        """Create a sample flow."""
        return {
            "id": "test-flow",
            "name": "Test Flow",
            "data": {
                "nodes": [
                    {
                        "id": "input",
                        "data": {
                            "node": {
                                "template": {
                                    "input_value": {"value": ""}
                                }
                            }
                        }
                    },
                    {
                        "id": "agent",
                        "data": {
                            "node": {
                                "template": {
                                    "temperature": {"value": 0.7},
                                    "model_name": {"value": "gpt-4"}
                                }
                            }
                        }
                    }
                ]
            }
        }

    def test_run_basic_success(self, cli_runner, mock_config, sample_flow):
        """Test basic flow execution."""
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            # Mock API
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api.run_flow = AsyncMock(return_value={
                "success": True,
                "outputs": {"result": "42"}
            })
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, ['test-flow'])
            
            assert result.exit_code == 0
            assert "Flow executed successfully" in result.output
            assert "42" in result.output

    def test_run_with_input_string(self, cli_runner, mock_config):
        """Test running with inline input."""
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.run_flow = AsyncMock(return_value={
                "success": True,
                "outputs": {"answer": "4"}
            })
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, [
                'test-flow',
                '--input', '{"question": "What is 2+2?"}'
            ])
            
            assert result.exit_code == 0
            
            # Verify input was passed correctly
            call_args = mock_api.run_flow.call_args
            assert call_args[0][1] == {"question": "What is 2+2?"}

    def test_run_with_input_file(self, cli_runner, mock_config):
        """Test running with input from file."""
        input_data = {"question": "What is the meaning of life?", "context": "Deep thought"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(input_data, f)
            f.flush()
            
            with patch('src.commands.run.Config.load', return_value=mock_config), \
                 patch('src.commands.run.StudioAPI') as mock_api_class:
                
                mock_api = Mock()
                mock_api.run_flow = AsyncMock(return_value={
                    "success": True,
                    "outputs": {"answer": "42"}
                })
                mock_api_class.return_value = mock_api
                
                result = cli_runner.invoke(run, [
                    'test-flow',
                    '--file', f.name
                ])
                
                assert result.exit_code == 0
                
                # Verify input was loaded from file
                call_args = mock_api.run_flow.call_args
                assert call_args[0][1] == input_data
                
            os.unlink(f.name)

    def test_run_with_output_file(self, cli_runner, mock_config):
        """Test saving output to file."""
        output_data = {"result": "Success", "data": [1, 2, 3]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
            
        try:
            with patch('src.commands.run.Config.load', return_value=mock_config), \
                 patch('src.commands.run.StudioAPI') as mock_api_class:
                
                mock_api = Mock()
                mock_api.run_flow = AsyncMock(return_value={
                    "success": True,
                    "outputs": output_data
                })
                mock_api_class.return_value = mock_api
                
                result = cli_runner.invoke(run, [
                    'test-flow',
                    '--output', output_file
                ])
                
                assert result.exit_code == 0
                assert f"Output saved to {output_file}" in result.output
                
                # Verify output was saved
                with open(output_file, 'r') as f:
                    saved_data = json.load(f)
                    assert saved_data == output_data
                    
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_run_with_tweaks(self, cli_runner, mock_config, sample_flow):
        """Test running with runtime tweaks."""
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api.update_flow = AsyncMock(return_value=True)
            mock_api.run_flow = AsyncMock(return_value={
                "success": True,
                "outputs": {}
            })
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, [
                'test-flow',
                '--tweak', 'agent.temperature=0.3',
                '--tweak', 'agent.max_tokens=2000'
            ])
            
            assert result.exit_code == 0
            assert "Applied 2 tweaks" in result.output
            assert "agent.temperature = 0.3" in result.output
            assert "agent.max_tokens = 2000" in result.output

    def test_run_with_variables(self, cli_runner, mock_config, sample_flow):
        """Test running with runtime variables."""
        # Modify sample flow to have variables
        sample_flow['data']['nodes'][1]['data']['node']['template']['model_name']['value'] = '{model}'
        
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api.update_flow = AsyncMock(return_value=True)
            mock_api.run_flow = AsyncMock(return_value={
                "success": True,
                "outputs": {}
            })
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, [
                'test-flow',
                '--var', 'model=gpt-4-turbo',
                '--var', 'temperature=0.5'
            ])
            
            assert result.exit_code == 0
            assert "Applying runtime modifications" in result.output

    def test_run_with_var_file(self, cli_runner, mock_config, sample_flow):
        """Test running with variables from file."""
        var_data = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(var_data, f)
            f.flush()
            
            with patch('src.commands.run.Config.load', return_value=mock_config), \
                 patch('src.commands.run.StudioAPI') as mock_api_class:
                
                mock_api = Mock()
                mock_api.get_flow = AsyncMock(return_value=sample_flow)
                mock_api.update_flow = AsyncMock(return_value=True)
                mock_api.run_flow = AsyncMock(return_value={
                    "success": True,
                    "outputs": {}
                })
                mock_api_class.return_value = mock_api
                
                result = cli_runner.invoke(run, [
                    'test-flow',
                    '--var-file', f.name
                ])
                
                assert result.exit_code == 0
                assert f"Loaded variables from {f.name}" in result.output
                
            os.unlink(f.name)

    def test_run_with_stream(self, cli_runner, mock_config):
        """Test running with streaming output."""
        stream_events = [
            {"type": "token", "token": "The "},
            {"type": "token", "token": "answer "},
            {"type": "token", "token": "is "},
            {"type": "token", "token": "42."},
            {"type": "result", "data": {"final": "The answer is 42."}}
        ]
        
        async def mock_stream(*args, **kwargs):
            for event in stream_events:
                yield event
        
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.run_flow_stream = mock_stream
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, [
                'test-flow',
                '--stream'
            ])
            
            assert result.exit_code == 0
            assert "Streaming output:" in result.output
            assert "The answer is 42." in result.output

    def test_run_flow_not_found(self, cli_runner, mock_config):
        """Test running non-existent flow."""
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=None)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, [
                'nonexistent-flow',
                '--tweak', 'agent.temperature=0.5'
            ])
            
            assert result.exit_code == 1
            assert "not found" in result.output

    def test_run_execution_failure(self, cli_runner, mock_config):
        """Test handling execution failures."""
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.run_flow = AsyncMock(return_value={
                "success": False,
                "error": "LLM API rate limit exceeded"
            })
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, ['test-flow'])
            
            assert result.exit_code == 0  # Command itself succeeds
            assert "Flow execution failed" in result.output
            assert "LLM API rate limit exceeded" in result.output

    def test_run_invalid_input_json(self, cli_runner, mock_config):
        """Test with invalid JSON input."""
        result = cli_runner.invoke(run, [
            'test-flow',
            '--input', 'invalid json{'
        ])
        
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    def test_run_invalid_tweak_format(self, cli_runner, mock_config):
        """Test with invalid tweak format."""
        result = cli_runner.invoke(run, [
            'test-flow',
            '--tweak', 'invalid_format'
        ])
        
        assert result.exit_code == 1
        assert "Invalid tweak format" in result.output

    def test_run_timeout(self, cli_runner, mock_config):
        """Test with custom timeout."""
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.run_flow = AsyncMock(return_value={
                "success": True,
                "outputs": {}
            })
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, [
                'test-flow',
                '--timeout', '60'
            ])
            
            assert result.exit_code == 0
            
            # Verify timeout was passed
            call_args = mock_api.run_flow.call_args
            assert call_args[1]['timeout'] == 60

    def test_deep_merge_function(self):
        """Test the _deep_merge helper function."""
        target = {
            "a": 1,
            "b": {"x": 1, "y": 2},
            "c": [1, 2]
        }
        source = {
            "b": {"y": 3, "z": 4},
            "d": 5
        }
        
        _deep_merge(target, source)
        
        assert target == {
            "a": 1,
            "b": {"x": 1, "y": 3, "z": 4},
            "c": [1, 2],
            "d": 5
        }

    def test_display_result_to_stdout(self):
        """Test displaying result to stdout."""
        result = {"key": "value", "number": 42}
        
        with patch('builtins.print') as mock_print:
            _display_result(result, None)
            
            # Should print formatted JSON
            print_calls = [str(call[0][0]) for call in mock_print.call_args_list if call[0]]
            full_output = '\n'.join(print_calls)
            assert '"key": "value"' in full_output
            assert '"number": 42' in full_output

    def test_display_result_to_file(self):
        """Test saving result to file."""
        result = {"test": "data"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
            
        try:
            with patch('click.echo') as mock_echo:
                _display_result(result, output_file)
                
                # Check file was written
                with open(output_file, 'r') as f:
                    saved_data = json.load(f)
                    assert saved_data == result
                
                # Check message was displayed
                mock_echo.assert_called_with(f"Output saved to {output_file}")
                
        finally:
            os.unlink(output_file)

    def test_run_stream_with_error(self, cli_runner, mock_config):
        """Test streaming with error event."""
        async def mock_stream(*args, **kwargs):
            yield {"type": "token", "token": "Processing..."}
            yield {"type": "error", "message": "API Error occurred"}
        
        with patch('src.commands.run.Config.load', return_value=mock_config), \
             patch('src.commands.run.StudioAPI') as mock_api_class:
            
            mock_api = Mock()
            mock_api.run_flow_stream = mock_stream
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(run, ['test-flow', '--stream'])
            
            assert result.exit_code == 0
            assert "Processing..." in result.output
            assert "❌ Error: API Error occurred" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])