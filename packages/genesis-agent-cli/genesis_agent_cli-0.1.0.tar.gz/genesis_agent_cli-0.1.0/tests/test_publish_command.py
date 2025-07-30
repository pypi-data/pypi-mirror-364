"""
Unit tests for the Publish command.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, mock_open, MagicMock
from click.testing import CliRunner
import docker
import json

from src.commands.publish import publish, build_docker_image, create_requirements_file, create_agent_script


class TestPublishCommand:
    """Test cases for publish command."""

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
        """Create a sample flow data."""
        return {
            "id": "test-flow-123",
            "name": "Test Agent",
            "description": "Test agent for publishing",
            "data": {
                "nodes": [
                    {
                        "id": "input",
                        "type": "ChatInput",
                        "data": {"type": "ChatInput"}
                    },
                    {
                        "id": "agent",
                        "type": "Agent",
                        "data": {
                            "type": "Agent",
                            "node": {
                                "template": {
                                    "agent_llm": {"value": "OpenAI"},
                                    "model_name": {"value": "gpt-4"}
                                }
                            }
                        }
                    }
                ],
                "edges": []
            }
        }

    def test_publish_basic_success(self, cli_runner, mock_config, sample_flow):
        """Test successful publishing of agent."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker, \
             patch('src.commands.publish.tempfile.mkdtemp', return_value='/tmp/test-build'), \
             patch('src.commands.publish.shutil.rmtree'), \
             patch('builtins.open', mock_open()):
            
            # Mock API service
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            # Mock Docker client
            mock_docker_client = Mock()
            mock_image = Mock()
            mock_image.tags = ['myorg/agent:v1']
            mock_docker_client.images.build.return_value = (mock_image, [])
            mock_docker.return_value = mock_docker_client
            
            result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'myorg/agent:v1'])
            
            assert result.exit_code == 0
            assert "Successfully built" in result.output
            assert "myorg/agent:v1" in result.output
            
            # Verify API was called
            mock_api.get_flow.assert_called_once_with('test-flow-123')
            
            # Verify Docker build was called
            mock_docker_client.images.build.assert_called_once()

    def test_publish_with_push(self, cli_runner, mock_config, sample_flow):
        """Test publishing and pushing to registry."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker, \
             patch('src.commands.publish.tempfile.mkdtemp', return_value='/tmp/test-build'), \
             patch('src.commands.publish.shutil.rmtree'), \
             patch('builtins.open', mock_open()):
            
            # Mock API service
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            # Mock Docker client
            mock_docker_client = Mock()
            mock_image = Mock()
            mock_image.tags = ['myorg/agent:v1']
            mock_docker_client.images.build.return_value = (mock_image, [])
            mock_docker_client.images.push.return_value = []
            mock_docker.return_value = mock_docker_client
            
            result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'myorg/agent:v1', '--push'])
            
            assert result.exit_code == 0
            assert "Successfully built" in result.output
            assert "Pushing image" in result.output
            assert "Successfully pushed" in result.output
            
            # Verify push was called
            mock_docker_client.images.push.assert_called_with('myorg/agent:v1')

    def test_publish_custom_base_image(self, cli_runner, mock_config, sample_flow):
        """Test publishing with custom base image."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker, \
             patch('src.commands.publish.tempfile.mkdtemp', return_value='/tmp/test-build'), \
             patch('src.commands.publish.shutil.rmtree'), \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            mock_docker_client = Mock()
            mock_image = Mock()
            mock_image.tags = ['myorg/agent:v1']
            mock_docker_client.images.build.return_value = (mock_image, [])
            mock_docker.return_value = mock_docker_client
            
            result = cli_runner.invoke(publish, [
                'test-flow-123',
                '-t', 'myorg/agent:v1',
                '--base-image', 'python:3.11-slim'
            ])
            
            assert result.exit_code == 0
            
            # Check that Dockerfile was created with custom base image
            dockerfile_content = mock_file.return_value.write.call_args_list
            dockerfile_str = ''.join([call[0][0] for call in dockerfile_content])
            assert 'FROM python:3.11-slim' in dockerfile_str

    def test_publish_flow_not_found(self, cli_runner, mock_config):
        """Test publishing non-existent flow."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(side_effect=Exception("404 Not Found"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(publish, ['nonexistent-flow', '-t', 'myorg/agent:v1'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "404 Not Found" in result.output

    def test_publish_docker_not_available(self, cli_runner, mock_config, sample_flow):
        """Test handling when Docker is not available."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            # Mock Docker not available
            mock_docker.side_effect = docker.errors.DockerException("Docker daemon not running")
            
            result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'myorg/agent:v1'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "Docker" in result.output

    def test_publish_invalid_tag_format(self, cli_runner, mock_config):
        """Test publishing with invalid Docker tag format."""
        result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'invalid tag with spaces'])
        
        # Should fail due to invalid tag format
        assert result.exit_code != 0

    def test_create_requirements_file(self):
        """Test requirements.txt file creation."""
        build_dir = tempfile.mkdtemp()
        
        try:
            create_requirements_file(build_dir)
            
            req_file = os.path.join(build_dir, 'requirements.txt')
            assert os.path.exists(req_file)
            
            with open(req_file, 'r') as f:
                content = f.read()
                assert 'langflow' in content
                assert 'httpx' in content
                assert 'pydantic' in content
        finally:
            import shutil
            shutil.rmtree(build_dir)

    def test_create_agent_script(self, sample_flow):
        """Test agent.py script creation."""
        build_dir = tempfile.mkdtemp()
        
        try:
            create_agent_script(build_dir, sample_flow)
            
            script_file = os.path.join(build_dir, 'agent.py')
            assert os.path.exists(script_file)
            
            with open(script_file, 'r') as f:
                content = f.read()
                assert 'import json' in content
                assert 'from langflow' in content
                assert 'flow_data = ' in content
                assert sample_flow['id'] in content
        finally:
            import shutil
            shutil.rmtree(build_dir)

    def test_build_docker_image_with_logs(self):
        """Test Docker image building with build logs."""
        build_dir = tempfile.mkdtemp()
        tag = "test:latest"
        base_image = "python:3.9-slim"
        
        try:
            # Create required files
            with open(os.path.join(build_dir, 'Dockerfile'), 'w') as f:
                f.write(f"FROM {base_image}\n")
            
            with patch('src.commands.publish.docker.from_env') as mock_docker:
                mock_client = Mock()
                mock_image = Mock()
                mock_image.tags = [tag]
                
                # Mock build logs
                build_logs = [
                    {"stream": "Step 1/5 : FROM python:3.9-slim\n"},
                    {"stream": "Step 2/5 : WORKDIR /app\n"},
                    {"stream": "Successfully built abc123\n"}
                ]
                
                mock_client.images.build.return_value = (mock_image, build_logs)
                mock_docker.return_value = mock_client
                
                image = build_docker_image(build_dir, tag, base_image)
                
                assert image == mock_image
                mock_client.images.build.assert_called_once()
                
        finally:
            import shutil
            shutil.rmtree(build_dir)

    def test_publish_with_env_vars(self, cli_runner, mock_config, sample_flow):
        """Test publishing with environment variables in flow."""
        # Add env vars to flow
        sample_flow['data']['nodes'][1]['data']['node']['template']['api_key'] = {
            'value': '${OPENAI_API_KEY}'
        }
        
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker, \
             patch('src.commands.publish.tempfile.mkdtemp', return_value='/tmp/test-build'), \
             patch('src.commands.publish.shutil.rmtree'), \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            mock_docker_client = Mock()
            mock_image = Mock()
            mock_image.tags = ['myorg/agent:v1']
            mock_docker_client.images.build.return_value = (mock_image, [])
            mock_docker.return_value = mock_docker_client
            
            result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'myorg/agent:v1'])
            
            assert result.exit_code == 0
            
            # Check that Dockerfile includes ENV instruction
            dockerfile_content = mock_file.return_value.write.call_args_list
            dockerfile_str = ''.join([call[0][0] for call in dockerfile_content])
            assert 'ENV ' in dockerfile_str or '${OPENAI_API_KEY}' in dockerfile_str

    def test_publish_build_failure(self, cli_runner, mock_config, sample_flow):
        """Test handling of Docker build failures."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker, \
             patch('src.commands.publish.tempfile.mkdtemp', return_value='/tmp/test-build'), \
             patch('src.commands.publish.shutil.rmtree'), \
             patch('builtins.open', mock_open()):
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            # Mock Docker build failure
            mock_docker_client = Mock()
            mock_docker_client.images.build.side_effect = docker.errors.BuildError(
                "Build failed", 
                [{"error": "Package not found"}]
            )
            mock_docker.return_value = mock_docker_client
            
            result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'myorg/agent:v1'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "Build failed" in result.output

    def test_publish_push_failure(self, cli_runner, mock_config, sample_flow):
        """Test handling of Docker push failures."""
        with patch('src.commands.publish.Config', return_value=mock_config), \
             patch('src.commands.publish.APIService') as mock_api_class, \
             patch('src.commands.publish.docker.from_env') as mock_docker, \
             patch('src.commands.publish.tempfile.mkdtemp', return_value='/tmp/test-build'), \
             patch('src.commands.publish.shutil.rmtree'), \
             patch('builtins.open', mock_open()):
            
            mock_api = Mock()
            mock_api.get_flow = AsyncMock(return_value=sample_flow)
            mock_api_class.return_value = mock_api
            
            # Mock successful build but failed push
            mock_docker_client = Mock()
            mock_image = Mock()
            mock_image.tags = ['myorg/agent:v1']
            mock_docker_client.images.build.return_value = (mock_image, [])
            mock_docker_client.images.push.side_effect = docker.errors.APIError("Authentication required")
            mock_docker.return_value = mock_docker_client
            
            result = cli_runner.invoke(publish, ['test-flow-123', '-t', 'myorg/agent:v1', '--push'])
            
            assert result.exit_code == 1
            assert "Error pushing" in result.output
            assert "Authentication" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])