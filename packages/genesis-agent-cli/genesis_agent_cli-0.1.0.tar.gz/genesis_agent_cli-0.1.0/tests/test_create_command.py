"""
Unit tests for the Create command.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from click.testing import CliRunner
from pathlib import Path

from src.commands.create import create, CreateResult, handle_validation_only
from src.services.config import Config
from src.models.agent_spec_enhanced import AgentSpecV2Enhanced


class TestCreateCommand:
    """Test cases for create command."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.genesis_studio_url = "http://test.example.com"
        config.api_key = "test-api-key"
        return config

    @pytest.fixture
    def sample_template(self):
        """Create a sample template file."""
        content = """
name: "Test Agent"
components:
  - id: "input"
    type: "genesis:chat_input"
    provides:
      - in: "agent"
        useAs: "input"
  - id: "agent"
    type: "genesis:agent"
    config:
      agent_llm: "Azure OpenAI"
      model_name: "gpt-4"
  - id: "output"
    type: "genesis:chat_output"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            f.flush()
            return f.name

    @pytest.fixture
    def sample_enhanced_template(self):
        """Create a sample enhanced template file."""
        content = """
id: "urn:agent:genesis:test:1"
name: "Test Enhanced Agent"
fullyQualifiedName: "genesis.autonomize.ai.test"
description: "Test agent"
domain: "autonomize.ai"
subDomain: "test"
version: "1.0.0"
environment: "production"
agentOwner: "test@example.com"
agentOwnerDisplayName: "Test Team"
email: "test@example.com"
status: "ACTIVE"
kind: "Single Agent"
agentGoal: "Test operations"
targetUser: "internal"
valueGeneration: "ProcessAutomation"
interactionMode: "RequestResponse"
runMode: "RealTime"
agencyLevel: "ModelDrivenWorkflow"
toolsUse: true
learningCapability: "None"
components:
  - id: "agent"
    type: "genesis:agent"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            f.flush()
            return f.name

    def test_create_basic_success(self, cli_runner, sample_template, mock_config):
        """Test successful creation of basic agent."""
        mock_flow = {
            "id": "test-flow-id",
            "name": "Test Agent",
            "data": {"nodes": [], "edges": []}
        }
        
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = mock_flow
            
            result = cli_runner.invoke(create, ['-t', sample_template])
            
            assert result.exit_code == 0
            assert "successfully created" in result.output
            assert "test-flow-id" in result.output
            
            # Verify the create function was called
            mock_create.assert_called_once()
            
        # Cleanup
        os.unlink(sample_template)

    def test_create_with_name_override(self, cli_runner, sample_template, mock_config):
        """Test creation with custom name."""
        mock_flow = {
            "id": "test-flow-id",
            "name": "Custom Name",
            "data": {"nodes": [], "edges": []}
        }
        
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = mock_flow
            
            result = cli_runner.invoke(create, ['-t', sample_template, '-n', 'Custom Name'])
            
            assert result.exit_code == 0
            assert "Custom Name" in result.output
            
        os.unlink(sample_template)

    def test_create_with_folder(self, cli_runner, sample_template, mock_config):
        """Test creation in specific folder."""
        mock_flow = {
            "id": "test-flow-id",
            "name": "Test Agent",
            "data": {"nodes": [], "edges": []}
        }
        
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = mock_flow
            
            result = cli_runner.invoke(create, ['-t', sample_template, '-f', 'folder-123'])
            
            assert result.exit_code == 0
            
            # Check that folder_id was passed
            call_args = mock_create.call_args[1]
            assert call_args.get('folder_id') == 'folder-123'
            
        os.unlink(sample_template)

    def test_create_with_variables(self, cli_runner, sample_template, mock_config):
        """Test creation with runtime variables."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = {"id": "test-id", "name": "Test"}
            
            result = cli_runner.invoke(create, [
                '-t', sample_template,
                '--var', 'temperature=0.5',
                '--var', 'model=gpt-4'
            ])
            
            assert result.exit_code == 0
            
            # Check that variables were passed
            call_args = mock_create.call_args[1]
            assert call_args.get('variables') == {'temperature': '0.5', 'model': 'gpt-4'}
            
        os.unlink(sample_template)

    def test_create_with_var_file(self, cli_runner, sample_template, mock_config):
        """Test creation with variables from file."""
        var_file_content = {
            "temperature": 0.7,
            "model": "gpt-4",
            "max_tokens": 2000
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as var_file:
            json.dump(var_file_content, var_file)
            var_file.flush()
            
            with patch('src.commands.create.Config', return_value=mock_config), \
                 patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
                
                mock_create.return_value = {"id": "test-id", "name": "Test"}
                
                result = cli_runner.invoke(create, [
                    '-t', sample_template,
                    '--var-file', var_file.name
                ])
                
                assert result.exit_code == 0
                
                # Check that variables were loaded from file
                call_args = mock_create.call_args[1]
                assert call_args.get('variables') == var_file_content
                
            os.unlink(var_file.name)
            
        os.unlink(sample_template)

    def test_create_with_tweaks(self, cli_runner, sample_template, mock_config):
        """Test creation with tweaks."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = {"id": "test-id", "name": "Test"}
            
            result = cli_runner.invoke(create, [
                '-t', sample_template,
                '--tweak', 'agent.temperature=0.3',
                '--tweak', 'agent.max_tokens=1500'
            ])
            
            assert result.exit_code == 0
            
            # Check that tweaks were parsed correctly
            call_args = mock_create.call_args[1]
            tweaks = call_args.get('tweaks')
            assert tweaks == {
                'agent': {
                    'temperature': '0.3',
                    'max_tokens': '1500'
                }
            }
            
        os.unlink(sample_template)

    def test_create_save_to_file(self, cli_runner, sample_template, mock_config):
        """Test saving flow to file instead of creating."""
        mock_flow = {
            "id": "test-flow-id",
            "name": "Test Agent",
            "data": {"nodes": [], "edges": []}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            with patch('src.commands.create.Config', return_value=mock_config), \
                 patch('src.commands.create.FlowConverter') as mock_converter_class:
                
                # Mock the converter instance
                mock_converter = Mock()
                mock_converter.convert_sync.return_value = mock_flow
                mock_converter_class.return_value = mock_converter
                
                result = cli_runner.invoke(create, [
                    '-t', sample_template,
                    '-o', output_file.name
                ])
                
                assert result.exit_code == 0
                assert f"saved to {output_file.name}" in result.output
                
                # Verify file was written
                with open(output_file.name, 'r') as f:
                    saved_data = json.load(f)
                    assert saved_data == mock_flow
                    
            os.unlink(output_file.name)
            
        os.unlink(sample_template)

    def test_create_validate_only(self, cli_runner, sample_template, mock_config):
        """Test validation-only mode."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.FlowConverter') as mock_converter_class, \
             patch('src.commands.create.ComponentValidator') as mock_validator_class:
            
            # Mock converter
            mock_converter = Mock()
            mock_converter.parser.parse_specification.return_value = {"name": "Test"}
            mock_converter_class.return_value = mock_converter
            
            # Mock validator
            mock_validator = Mock()
            mock_validator.validate_spec = AsyncMock(return_value={
                "valid": True,
                "errors": [],
                "warnings": [],
                "missing_components": []
            })
            mock_validator_class.return_value = mock_validator
            
            result = cli_runner.invoke(create, [
                '-t', sample_template,
                '--validate-only'
            ])
            
            assert result.exit_code == 0
            assert "Validation passed" in result.output
            
        os.unlink(sample_template)

    def test_create_validation_errors(self, cli_runner, sample_template, mock_config):
        """Test handling validation errors."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.FlowConverter') as mock_converter_class, \
             patch('src.commands.create.ComponentValidator') as mock_validator_class:
            
            # Mock converter
            mock_converter = Mock()
            mock_converter.parser.parse_specification.return_value = {"name": "Test"}
            mock_converter_class.return_value = mock_converter
            
            # Mock validator with errors
            mock_validator = Mock()
            mock_validator.validate_spec = AsyncMock(return_value={
                "valid": False,
                "errors": ["Component 'genesis:unknown' not found"],
                "warnings": ["Deprecated component 'genesis:old'"],
                "missing_components": ["genesis:unknown"]
            })
            mock_validator_class.return_value = mock_validator
            
            result = cli_runner.invoke(create, [
                '-t', sample_template,
                '--validate-only'
            ])
            
            assert result.exit_code == 1
            assert "Validation failed" in result.output
            assert "Component 'genesis:unknown' not found" in result.output
            assert "Deprecated component 'genesis:old'" in result.output
            
        os.unlink(sample_template)

    def test_create_show_metadata(self, cli_runner, sample_enhanced_template, mock_config):
        """Test showing agent metadata."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.FlowConverter') as mock_converter_class, \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            # Mock converter that returns enhanced spec
            mock_converter = Mock()
            mock_spec = AgentSpecV2Enhanced(
                id="urn:agent:genesis:test:1",
                name="Test Enhanced Agent",
                fullyQualifiedName="genesis.autonomize.ai.test",
                description="Test agent",
                domain="autonomize.ai",
                subDomain="test",
                version="1.0.0",
                environment="production",
                agentOwner="test@example.com",
                agentOwnerDisplayName="Test Team",
                email="test@example.com",
                status="ACTIVE",
                kind="Single Agent",
                agentGoal="Test operations",
                targetUser="internal",
                valueGeneration="ProcessAutomation",
                interactionMode="RequestResponse",
                runMode="RealTime",
                agencyLevel="ModelDrivenWorkflow",
                toolsUse=True,
                learningCapability="None",
                components=[],
                kpis=[{
                    "name": "Success Rate",
                    "category": "Quality",
                    "valueType": "percentage",
                    "target": 98
                }]
            )
            mock_converter.parser.parse_specification.return_value = mock_spec
            mock_converter_class.return_value = mock_converter
            
            mock_create.return_value = {"id": "test-id", "name": "Test"}
            
            result = cli_runner.invoke(create, [
                '-t', sample_enhanced_template,
                '--show-metadata'
            ])
            
            assert result.exit_code == 0
            assert "Agent Metadata" in result.output
            assert "Goal: Test operations" in result.output
            assert "Domain: autonomize.ai" in result.output
            assert "Agency Level: ModelDrivenWorkflow" in result.output
            assert "KPIs" in result.output
            assert "Success Rate" in result.output
            
        os.unlink(sample_enhanced_template)

    def test_create_with_debug(self, cli_runner, sample_template, mock_config):
        """Test creation with debug mode."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = {"id": "test-id", "name": "Test"}
            
            result = cli_runner.invoke(create, [
                '-t', sample_template,
                '--debug'
            ])
            
            assert result.exit_code == 0
            # Debug mode should show more verbose output
            assert "Creating flow from template" in result.output or len(result.output) > 50
            
        os.unlink(sample_template)

    def test_create_file_not_found(self, cli_runner):
        """Test handling of non-existent template file."""
        result = cli_runner.invoke(create, ['-t', 'nonexistent.yaml'])
        
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_create_invalid_yaml(self, cli_runner, mock_config):
        """Test handling of invalid YAML."""
        invalid_yaml = """
invalid yaml content:
  - missing quote
  - : invalid
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()
            
            with patch('src.commands.create.Config', return_value=mock_config):
                result = cli_runner.invoke(create, ['-t', f.name])
                
                assert result.exit_code == 1
                assert "Error" in result.output
                
            os.unlink(f.name)

    def test_create_api_error(self, cli_runner, sample_template, mock_config):
        """Test handling of API errors during creation."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.side_effect = Exception("API Error: 500 Internal Server Error")
            
            result = cli_runner.invoke(create, ['-t', sample_template])
            
            assert result.exit_code == 1
            assert "API Error" in result.output
            
        os.unlink(sample_template)

    def test_create_tweak_parsing(self, cli_runner):
        """Test tweak parsing logic."""
        from src.commands.create import parse_tweaks
        
        # Test single tweak
        tweaks = parse_tweaks(['agent.temperature=0.5'])
        assert tweaks == {'agent': {'temperature': '0.5'}}
        
        # Test multiple tweaks for same component
        tweaks = parse_tweaks([
            'agent.temperature=0.5',
            'agent.max_tokens=2000',
            'output.format=json'
        ])
        assert tweaks == {
            'agent': {
                'temperature': '0.5',
                'max_tokens': '2000'
            },
            'output': {
                'format': 'json'
            }
        }
        
        # Test invalid tweak format
        tweaks = parse_tweaks(['invalid_format'])
        assert tweaks == {}

    def test_handle_validation_only(self):
        """Test handle_validation_only function."""
        # Test successful validation
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": ["Minor warning"],
            "missing_components": []
        }
        
        result = handle_validation_only(validation_result)
        assert result == CreateResult.SUCCESS
        
        # Test failed validation
        validation_result = {
            "valid": False,
            "errors": ["Critical error"],
            "warnings": [],
            "missing_components": ["genesis:missing"]
        }
        
        result = handle_validation_only(validation_result)
        assert result == CreateResult.VALIDATION_ERROR

    def test_create_with_complex_variables(self, cli_runner, sample_template, mock_config):
        """Test creation with complex variable values."""
        with patch('src.commands.create.Config', return_value=mock_config), \
             patch('src.commands.create.create_flow_from_template', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = {"id": "test-id", "name": "Test"}
            
            result = cli_runner.invoke(create, [
                '-t', sample_template,
                '--var', 'config={"timeout": 30, "retries": 3}',
                '--var', 'tags=["test", "production"]',
                '--var', 'enabled=true'
            ])
            
            assert result.exit_code == 0
            
            # Check that complex variables were parsed
            call_args = mock_create.call_args[1]
            variables = call_args.get('variables')
            assert variables['config'] == '{"timeout": 30, "retries": 3}'
            assert variables['tags'] == '["test", "production"]'
            assert variables['enabled'] == 'true'
            
        os.unlink(sample_template)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])