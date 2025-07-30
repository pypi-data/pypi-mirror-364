"""
Unit tests for the Check Dependencies command.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner
from pathlib import Path

from src.commands.check_deps import check_deps, check_template_dependencies, check_all_templates, show_available_agents


class TestCheckDepsCommand:
    """Test cases for check-deps command."""

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
    def sample_template_with_deps(self):
        """Create a template with dependencies."""
        content = """
kind: "Multi Agent"
name: "Orchestrator Agent"
reusability:
  dependencies:
    - agentId: "urn:agent:genesis:document_processor:1"
      version: ">=1.0.0"
      required: true
    - agentId: "urn:agent:genesis:medication_extractor:1"
      version: ">=1.0.0"
      required: true
components:
  - id: "doc-processor"
    type: "$ref:document_processor"
    asTools: true
  - id: "med-extractor"
    type: "$ref:medication_extractor"
    asTools: true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            f.flush()
            return f.name

    @pytest.fixture
    def sample_template_no_deps(self):
        """Create a template without dependencies."""
        content = """
name: "Simple Agent"
components:
  - id: "agent"
    type: "genesis:agent"
    config:
      agent_llm: "OpenAI"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            f.flush()
            return f.name

    @pytest.fixture
    def available_agents(self):
        """Mock available agents data."""
        return [
            {
                "id": "urn:agent:genesis:document_processor:1",
                "name": "Document Processor",
                "version": "1.0.0",
                "fullyQualifiedName": "genesis.autonomize.ai.document_processor"
            },
            {
                "id": "urn:agent:genesis:medication_extractor:1",
                "name": "Medication Extractor",
                "version": "1.1.0",
                "fullyQualifiedName": "genesis.autonomize.ai.medication_extractor"
            },
            {
                "id": "urn:agent:genesis:clinical_validator:1",
                "name": "Clinical Validator",
                "version": "2.0.0",
                "fullyQualifiedName": "genesis.autonomize.ai.clinical_validator"
            }
        ]

    def test_check_deps_with_dependencies(self, cli_runner, mock_config, sample_template_with_deps, available_agents):
        """Test checking dependencies for template with deps."""
        with patch('src.commands.check_deps.Config', return_value=mock_config), \
             patch('src.commands.check_deps.APIService') as mock_api_class:
            
            # Mock API service
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=available_agents)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(check_deps, [sample_template_with_deps])
            
            assert result.exit_code == 0
            assert "Checking dependencies" in result.output
            assert "Document Processor" in result.output
            assert "Medication Extractor" in result.output
            assert "✓" in result.output  # Check marks for found dependencies
            
        os.unlink(sample_template_with_deps)

    def test_check_deps_no_dependencies(self, cli_runner, mock_config, sample_template_no_deps):
        """Test checking template without dependencies."""
        with patch('src.commands.check_deps.Config', return_value=mock_config):
            result = cli_runner.invoke(check_deps, [sample_template_no_deps])
            
            assert result.exit_code == 0
            assert "No dependencies found" in result.output
            
        os.unlink(sample_template_no_deps)

    def test_check_deps_missing_dependency(self, cli_runner, mock_config):
        """Test checking with missing dependency."""
        template_content = """
kind: "Multi Agent"
reusability:
  dependencies:
    - agentId: "urn:agent:genesis:missing_agent:1"
      version: ">=1.0.0"
      required: true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(template_content)
            f.flush()
            
            with patch('src.commands.check_deps.Config', return_value=mock_config), \
                 patch('src.commands.check_deps.APIService') as mock_api_class:
                
                mock_api = Mock()
                mock_api.list_flows = AsyncMock(return_value=[])  # No agents available
                mock_api_class.return_value = mock_api
                
                result = cli_runner.invoke(check_deps, [f.name])
                
                assert result.exit_code == 1
                assert "✗" in result.output  # X mark for missing dependency
                assert "missing_agent" in result.output
                
            os.unlink(f.name)

    def test_check_deps_version_mismatch(self, cli_runner, mock_config):
        """Test checking with version mismatch."""
        template_content = """
reusability:
  dependencies:
    - agentId: "urn:agent:genesis:old_agent:1"
      version: ">=2.0.0"
      required: true
"""
        available = [{
            "id": "urn:agent:genesis:old_agent:1",
            "name": "Old Agent",
            "version": "1.0.0"  # Version too low
        }]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(template_content)
            f.flush()
            
            with patch('src.commands.check_deps.Config', return_value=mock_config), \
                 patch('src.commands.check_deps.APIService') as mock_api_class:
                
                mock_api = Mock()
                mock_api.list_flows = AsyncMock(return_value=available)
                mock_api_class.return_value = mock_api
                
                result = cli_runner.invoke(check_deps, [f.name])
                
                # Should fail due to version mismatch
                assert result.exit_code == 1
                assert "version" in result.output.lower()
                
            os.unlink(f.name)

    def test_check_deps_all_templates(self, cli_runner, mock_config):
        """Test checking all templates."""
        with patch('src.commands.check_deps.Config', return_value=mock_config), \
             patch('src.commands.check_deps.Path.glob') as mock_glob, \
             patch('src.commands.check_deps.check_template_dependencies') as mock_check:
            
            # Mock finding template files
            mock_glob.return_value = [
                Path("templates/healthcare/agents/agent1.yaml"),
                Path("templates/healthcare/agents/agent2.yaml"),
                Path("templates/examples/agent3.yaml")
            ]
            
            # Mock dependency check results
            mock_check.side_effect = [
                (True, []),   # agent1 - all deps satisfied
                (False, ["Missing dep"]),  # agent2 - missing dependency
                (True, [])    # agent3 - all deps satisfied
            ]
            
            result = cli_runner.invoke(check_deps, ['--all'])
            
            assert result.exit_code == 0
            assert "Checking all templates" in result.output
            assert "agent1.yaml" in result.output
            assert "agent2.yaml" in result.output
            assert "agent3.yaml" in result.output
            assert "✓" in result.output  # Success marks
            assert "✗" in result.output  # Failure marks

    def test_check_deps_show_available(self, cli_runner, mock_config, available_agents):
        """Test showing available agents."""
        with patch('src.commands.check_deps.Config', return_value=mock_config), \
             patch('src.commands.check_deps.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(return_value=available_agents)
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(check_deps, ['--show-available'])
            
            assert result.exit_code == 0
            assert "Available Agents in Genesis Studio" in result.output
            assert "Document Processor" in result.output
            assert "Medication Extractor" in result.output
            assert "Clinical Validator" in result.output
            assert "1.0.0" in result.output
            assert "1.1.0" in result.output
            assert "2.0.0" in result.output

    def test_check_deps_file_not_found(self, cli_runner, mock_config):
        """Test with non-existent template file."""
        result = cli_runner.invoke(check_deps, ['nonexistent.yaml'])
        
        assert result.exit_code == 1
        assert "Error" in result.output
        assert "not found" in result.output.lower()

    def test_check_deps_invalid_yaml(self, cli_runner, mock_config):
        """Test with invalid YAML file."""
        invalid_yaml = """
invalid yaml content:
  - missing quote
  - : invalid
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()
            
            result = cli_runner.invoke(check_deps, [f.name])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            
            os.unlink(f.name)

    def test_check_deps_optional_dependency(self, cli_runner, mock_config):
        """Test checking optional dependencies."""
        template_content = """
reusability:
  dependencies:
    - agentId: "urn:agent:genesis:required_agent:1"
      version: ">=1.0.0"
      required: true
    - agentId: "urn:agent:genesis:optional_agent:1"
      version: ">=1.0.0"
      required: false
"""
        available = [{
            "id": "urn:agent:genesis:required_agent:1",
            "name": "Required Agent",
            "version": "1.0.0"
        }]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(template_content)
            f.flush()
            
            with patch('src.commands.check_deps.Config', return_value=mock_config), \
                 patch('src.commands.check_deps.APIService') as mock_api_class:
                
                mock_api = Mock()
                mock_api.list_flows = AsyncMock(return_value=available)
                mock_api_class.return_value = mock_api
                
                result = cli_runner.invoke(check_deps, [f.name])
                
                # Should succeed even though optional dependency is missing
                assert result.exit_code == 0
                assert "optional" in result.output.lower()
                
            os.unlink(f.name)

    def test_check_template_dependencies_function(self, mock_config):
        """Test the check_template_dependencies function directly."""
        template_path = "test.yaml"
        spec = {
            "reusability": {
                "dependencies": [
                    {
                        "agentId": "urn:agent:genesis:test:1",
                        "version": ">=1.0.0",
                        "required": True
                    }
                ]
            }
        }
        available_agents = [{
            "id": "urn:agent:genesis:test:1",
            "version": "1.5.0"
        }]
        
        with patch('src.commands.check_deps.EnhancedSpecParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse_specification.return_value = spec
            mock_parser_class.return_value = mock_parser
            
            satisfied, missing = check_template_dependencies(
                template_path, available_agents
            )
            
            assert satisfied is True
            assert len(missing) == 0

    def test_show_available_agents_function(self, available_agents):
        """Test the show_available_agents function directly."""
        with patch('builtins.print') as mock_print:
            show_available_agents(available_agents)
            
            # Check that the function printed the header and agents
            print_calls = [str(call[0][0]) for call in mock_print.call_args_list]
            full_output = '\n'.join(print_calls)
            
            assert "Available Agents" in full_output
            assert "Document Processor" in full_output
            assert "genesis.autonomize.ai.document_processor" in full_output

    def test_check_deps_api_error(self, cli_runner, mock_config):
        """Test handling of API errors."""
        with patch('src.commands.check_deps.Config', return_value=mock_config), \
             patch('src.commands.check_deps.APIService') as mock_api_class:
            
            mock_api = Mock()
            mock_api.list_flows = AsyncMock(side_effect=Exception("API Error: 500"))
            mock_api_class.return_value = mock_api
            
            result = cli_runner.invoke(check_deps, ['--show-available'])
            
            assert result.exit_code == 1
            assert "Error" in result.output
            assert "500" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])