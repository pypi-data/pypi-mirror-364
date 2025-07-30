"""Test VariableResolver functionality."""

import pytest
import os
import json
import tempfile
from pathlib import Path

from src.services.variable_resolver import VariableResolver


class TestVariableResolver:
    """Test VariableResolver class."""
    
    def test_basic_variable_substitution(self):
        """Test basic variable substitution."""
        resolver = VariableResolver({"name": "test", "version": "1.0"})
        
        # Simple substitution
        assert resolver.resolve("{name}") == "test"
        assert resolver.resolve("{version}") == "1.0"
        
        # Embedded substitution
        assert resolver.resolve("Name: {name}") == "Name: test"
        assert resolver.resolve("{name}-{version}") == "test-1.0"
        
    def test_environment_variables(self):
        """Test environment variable substitution."""
        os.environ["TEST_VAR"] = "env_value"
        resolver = VariableResolver({})
        
        assert resolver.resolve("${TEST_VAR}") == "env_value"
        assert resolver.resolve("Env: ${TEST_VAR}") == "Env: env_value"
        
        # Cleanup
        del os.environ["TEST_VAR"]
        
    def test_nested_variables(self):
        """Test nested variable access."""
        variables = {
            "config": {
                "api_key": "test_key",
                "endpoint": "https://api.test.com"
            },
            "model": {
                "name": "gpt-4",
                "params": {
                    "temperature": 0.7
                }
            }
        }
        resolver = VariableResolver(variables)
        
        assert resolver.resolve("{config.api_key}") == "test_key"
        assert resolver.resolve("{model.name}") == "gpt-4"
        assert resolver.resolve("{model.params.temperature}") == 0.7
        
    def test_type_preservation(self):
        """Test that types are preserved when entire value is a variable."""
        variables = {
            "port": 8080,
            "temperature": 0.7,
            "enabled": True,
            "items": ["a", "b", "c"],
            "config": {"key": "value"}
        }
        resolver = VariableResolver(variables)
        
        # Direct variable references preserve type
        assert resolver.resolve("{port}") == 8080
        assert isinstance(resolver.resolve("{port}"), int)
        
        assert resolver.resolve("{temperature}") == 0.7
        assert isinstance(resolver.resolve("{temperature}"), float)
        
        assert resolver.resolve("{enabled}") is True
        assert isinstance(resolver.resolve("{enabled}"), bool)
        
        assert resolver.resolve("{items}") == ["a", "b", "c"]
        assert isinstance(resolver.resolve("{items}"), list)
        
        assert resolver.resolve("{config}") == {"key": "value"}
        assert isinstance(resolver.resolve("{config}"), dict)
        
        # Embedded variables are converted to strings
        assert resolver.resolve("Port: {port}") == "Port: 8080"
        assert isinstance(resolver.resolve("Port: {port}"), str)
        
    def test_undefined_variables(self):
        """Test handling of undefined variables."""
        resolver = VariableResolver({"defined": "value"})
        
        # Undefined variables are left as-is
        assert resolver.resolve("{undefined}") == "{undefined}"
        assert "undefined" in resolver.undefined_vars
        
        # Mixed defined and undefined
        assert resolver.resolve("{defined} and {undefined}") == "value and {undefined}"
        
    def test_dict_resolution(self):
        """Test resolving variables in dictionaries."""
        variables = {
            "name": "test_agent",
            "model": "gpt-4",
            "temp": 0.7
        }
        resolver = VariableResolver(variables)
        
        config = {
            "agent_name": "{name}",
            "llm": {
                "model": "{model}",
                "temperature": "{temp}",
                "max_tokens": 2000
            }
        }
        
        resolved = resolver.resolve_dict(config)
        
        assert resolved["agent_name"] == "test_agent"
        assert resolved["llm"]["model"] == "gpt-4"
        assert resolved["llm"]["temperature"] == 0.7
        assert resolved["llm"]["max_tokens"] == 2000
        
    def test_list_resolution(self):
        """Test resolving variables in lists."""
        variables = {"tag1": "healthcare", "tag2": "ai"}
        resolver = VariableResolver(variables)
        
        tags = ["{tag1}", "{tag2}", "static_tag"]
        resolved = resolver.resolve_list(tags)
        
        assert resolved == ["healthcare", "ai", "static_tag"]
        
    def test_tweaks(self):
        """Test applying tweaks to flows."""
        flow = {
            "data": {
                "nodes": [
                    {
                        "id": "agent-1",
                        "data": {
                            "node": {
                                "template": {
                                    "temperature": {"value": 0.7},
                                    "model_name": {"value": "gpt-3.5"}
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        resolver = VariableResolver({})
        resolver.tweaks = {
            "agent-1.temperature": "0.3",
            "agent-1.model_name": "gpt-4"
        }
        
        resolved = resolver.apply_tweaks(flow)
        
        node = resolved["data"]["nodes"][0]
        assert node["data"]["node"]["template"]["temperature"]["value"] == 0.3
        assert node["data"]["node"]["template"]["model_name"]["value"] == "gpt-4"
        
    def test_load_from_file(self):
        """Test loading variables from file."""
        # Test JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"var1": "value1", "var2": 123}, f)
            json_file = f.name
            
        # Test YAML file
        yaml_content = """
var1: value1
var2: 123
nested:
  key: value
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name
            
        try:
            # Load from JSON
            json_vars = VariableResolver.load_from_file(json_file)
            assert json_vars["var1"] == "value1"
            assert json_vars["var2"] == 123
            
            # Load from YAML
            yaml_vars = VariableResolver.load_from_file(yaml_file)
            assert yaml_vars["var1"] == "value1"
            assert yaml_vars["var2"] == 123
            assert yaml_vars["nested"]["key"] == "value"
            
        finally:
            # Cleanup
            os.unlink(json_file)
            os.unlink(yaml_file)
            
    def test_parse_var_string(self):
        """Test parsing variable strings from CLI."""
        # Simple key=value
        assert VariableResolver.parse_var_string("name=test") == {"name": "test"}
        
        # Numeric values
        assert VariableResolver.parse_var_string("port=8080") == {"port": 8080}
        assert VariableResolver.parse_var_string("temp=0.7") == {"temp": 0.7}
        
        # Boolean values
        assert VariableResolver.parse_var_string("enabled=true") == {"enabled": True}
        assert VariableResolver.parse_var_string("debug=false") == {"debug": False}
        
        # Nested values using dot notation
        result = VariableResolver.parse_var_string("config.api_key=test123")
        assert result == {"config": {"api_key": "test123"}}
        
        # Deep nesting
        result = VariableResolver.parse_var_string("a.b.c=value")
        assert result == {"a": {"b": {"c": "value"}}}
        
    def test_complex_scenario(self):
        """Test complex scenario with multiple features."""
        # Set environment variable
        os.environ["API_KEY"] = "secret_key"
        
        variables = {
            "agent_name": "TestAgent",
            "model": {
                "provider": "OpenAI",
                "name": "gpt-4"
            },
            "temperature": 0.7
        }
        
        resolver = VariableResolver(variables)
        
        # Complex configuration
        config = {
            "name": "{agent_name}",
            "api_key": "${API_KEY}",
            "llm_config": {
                "provider": "{model.provider}",
                "model": "{model.name}",
                "temperature": "{temperature}",
                "description": "Using {model.name} from {model.provider}"
            },
            "tags": ["{agent_name}", "production"]
        }
        
        resolved = resolver.resolve_dict(config)
        
        assert resolved["name"] == "TestAgent"
        assert resolved["api_key"] == "secret_key"
        assert resolved["llm_config"]["provider"] == "OpenAI"
        assert resolved["llm_config"]["model"] == "gpt-4"
        assert resolved["llm_config"]["temperature"] == 0.7
        assert resolved["llm_config"]["description"] == "Using gpt-4 from OpenAI"
        assert resolved["tags"] == ["TestAgent", "production"]
        
        # Cleanup
        del os.environ["API_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])