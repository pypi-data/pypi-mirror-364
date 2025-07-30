"""
Unit tests for the Enhanced Spec Parser module.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
import yaml

from src.parsers.enhanced_spec_parser import EnhancedSpecParser
from src.models.agent_spec_enhanced import (
    AgentSpecV2Enhanced, 
    AgencyLevel, 
    InteractionMode,
    RunMode,
    LearningCapability,
    TargetUser,
    ValueGeneration,
    Status,
    KPI,
    ValueType,
    Category
)


class TestEnhancedSpecParser:
    """Test cases for EnhancedSpecParser class."""

    @pytest.fixture
    def parser(self):
        """Create an EnhancedSpecParser instance."""
        return EnhancedSpecParser()

    @pytest.fixture
    def valid_enhanced_yaml(self):
        """Create a valid enhanced specification YAML content."""
        return """
id: "urn:agent:genesis:test:1"
name: "Test Agent"
fullyQualifiedName: "genesis.autonomize.ai.test"
description: "Test agent for unit testing"
domain: "autonomize.ai"
subDomain: "testing"
version: "1.0.0"
environment: "production"
agentOwner: "test@example.com"
agentOwnerDisplayName: "Test Team"
email: "test@example.com"
status: "ACTIVE"

tags:
  - "test"
  - "unit-test"

kind: "Single Agent"
agentGoal: "Perform unit testing operations"
targetUser: "internal"
valueGeneration: "ProcessAutomation"
interactionMode: "RequestResponse"
runMode: "RealTime"
agencyLevel: "ModelDrivenWorkflow"
toolsUse: true
learningCapability: "None"

kpis:
  - name: "Success Rate"
    category: "Quality"
    valueType: "percentage"
    target: 98
    unit: "%"
    description: "Percentage of successful operations"

components:
  - id: "input"
    name: "User Input"
    type: "genesis:chat_input"
    kind: "Data"
    description: "Receive user input"
    provides:
      - useAs: "input"
        in: "agent"
        description: "Connect to agent"
        
  - id: "agent"
    name: "Test Agent"
    type: "genesis:agent"
    kind: "Agent"
    config:
      agent_llm: "Azure OpenAI"
      model_name: "gpt-4"
      temperature: 0.7
      system_prompt: "You are a test agent"
    provides:
      - useAs: "input"
        in: "output"
        description: "Agent response"
        
  - id: "output"
    name: "Output"
    type: "genesis:chat_output"
    kind: "Data"

reusability:
  asTools: true
  standalone: true
  provides:
    toolName: "TestTool"
    toolDescription: "A test tool"
    inputSchema:
      type: "object"
      properties:
        query:
          type: "string"
    outputSchema:
      type: "object"
      properties:
        result:
          type: "string"
  dependencies:
    - agentId: "urn:agent:genesis:dependency:1"
      version: ">=1.0.0"
      required: true

sampleInput:
  query: "test query"
  data: {"key": "value"}

outputs:
  - "result"
  - "status"

securityInfo:
  visibility: "Private"
  confidentiality: "High"
  gdprSensitive: true
"""

    @pytest.fixture
    def valid_v2_yaml(self):
        """Create a valid v2 specification YAML content."""
        return """
name: "Simple Agent"
components:
  - id: "input"
    type: "genesis:chat_input"
    provides:
      - in: "agent"
        useAs: "input"
        
  - id: "agent"
    type: "genesis:agent"
    config:
      agent_llm: "OpenAI"
      model_name: "gpt-4"
      system_prompt: "You are a helpful assistant"
    provides:
      - in: "output"
        useAs: "input"
        
  - id: "output"
    type: "genesis:chat_output"
"""

    @pytest.fixture
    def invalid_yaml(self):
        """Create invalid YAML content."""
        return """
invalid yaml content:
  - missing quote
  - : invalid structure
"""

    def test_parser_initialization(self):
        """Test EnhancedSpecParser initialization."""
        parser = EnhancedSpecParser()
        assert parser is not None

    def test_parse_enhanced_specification(self, parser, valid_enhanced_yaml):
        """Test parsing a valid enhanced specification."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_enhanced_yaml)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                # Verify it's an enhanced spec
                assert isinstance(spec, AgentSpecV2Enhanced)
                assert spec.id == "urn:agent:genesis:test:1"
                assert spec.name == "Test Agent"
                assert spec.fullyQualifiedName == "genesis.autonomize.ai.test"
                assert spec.agentGoal == "Perform unit testing operations"
                assert spec.agencyLevel == AgencyLevel.MODEL_DRIVEN_WORKFLOW
                assert spec.targetUser == TargetUser.INTERNAL
                assert spec.valueGeneration == ValueGeneration.PROCESS_AUTOMATION
                assert spec.interactionMode == InteractionMode.REQUEST_RESPONSE
                assert spec.runMode == RunMode.REAL_TIME
                assert spec.learningCapability == LearningCapability.NONE
                assert spec.toolsUse is True
                
                # Verify tags
                assert len(spec.tags) == 2
                assert "test" in spec.tags
                assert "unit-test" in spec.tags
                
                # Verify KPIs
                assert len(spec.kpis) == 1
                kpi = spec.kpis[0]
                assert kpi.name == "Success Rate"
                assert kpi.category == Category.QUALITY
                assert kpi.valueType == ValueType.PERCENTAGE
                assert kpi.target == 98
                
                # Verify components
                assert len(spec.components) == 3
                assert spec.components[0]["id"] == "input"
                assert spec.components[1]["id"] == "agent"
                assert spec.components[2]["id"] == "output"
                
                # Verify reusability
                assert spec.reusability is not None
                assert spec.reusability["asTools"] is True
                assert spec.reusability["provides"]["toolName"] == "TestTool"
                assert len(spec.reusability["dependencies"]) == 1
                
                # Verify security info
                assert spec.securityInfo is not None
                assert spec.securityInfo["visibility"] == "Private"
                assert spec.securityInfo["gdprSensitive"] is True
                
            finally:
                os.unlink(f.name)

    def test_parse_v2_specification(self, parser, valid_v2_yaml):
        """Test parsing a v2 specification (non-enhanced)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(valid_v2_yaml)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                # Should return a dictionary for v2 specs
                assert isinstance(spec, dict)
                assert spec["name"] == "Simple Agent"
                assert len(spec["components"]) == 3
                assert spec["components"][0]["id"] == "input"
                assert spec["components"][1]["config"]["agent_llm"] == "OpenAI"
                
            finally:
                os.unlink(f.name)

    def test_parse_invalid_yaml(self, parser, invalid_yaml):
        """Test parsing invalid YAML content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()
            
            try:
                with pytest.raises(Exception) as exc_info:
                    parser.parse_specification(f.name)
                
                # Should raise a YAML parsing error
                assert "YAML" in str(exc_info.value) or "yaml" in str(exc_info.value)
                
            finally:
                os.unlink(f.name)

    def test_parse_nonexistent_file(self, parser):
        """Test parsing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            parser.parse_specification("/nonexistent/path/to/file.yaml")

    def test_parse_empty_file(self, parser):
        """Test parsing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                # Empty file should return None or empty dict
                assert spec is None or spec == {}
                
            finally:
                os.unlink(f.name)

    def test_parse_specification_with_missing_required_fields(self, parser):
        """Test parsing enhanced spec with missing required fields."""
        yaml_content = """
id: "test-id"
name: "Test"
# Missing required fields like agentGoal, targetUser, etc.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                with pytest.raises(Exception) as exc_info:
                    spec = parser.parse_specification(f.name)
                
                # Should raise validation error for missing fields
                assert "field required" in str(exc_info.value).lower() or \
                       "missing" in str(exc_info.value).lower()
                
            finally:
                os.unlink(f.name)

    def test_parse_specification_with_invalid_enum_values(self, parser):
        """Test parsing enhanced spec with invalid enum values."""
        yaml_content = """
id: "test-id"
name: "Test"
fullyQualifiedName: "test.fqn"
description: "Test"
domain: "test"
subDomain: "test"
version: "1.0.0"
environment: "test"
agentOwner: "test@test.com"
agentOwnerDisplayName: "Test"
email: "test@test.com"
status: "ACTIVE"
kind: "Single Agent"
agentGoal: "Test goal"
targetUser: "invalid_value"  # Invalid enum
valueGeneration: "ProcessAutomation"
interactionMode: "RequestResponse"
runMode: "RealTime"
agencyLevel: "ModelDrivenWorkflow"
toolsUse: true
learningCapability: "None"
components: []
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                with pytest.raises(Exception) as exc_info:
                    spec = parser.parse_specification(f.name)
                
                # Should raise validation error for invalid enum
                assert "invalid" in str(exc_info.value).lower() or \
                       "not a valid" in str(exc_info.value).lower()
                
            finally:
                os.unlink(f.name)

    def test_parse_specification_with_variables(self, parser):
        """Test parsing specification with variables."""
        yaml_content = """
name: "{agent_name}"
components:
  - id: "agent"
    type: "genesis:agent"
    config:
      agent_llm: "{llm_provider}"
      model_name: "{model_name}"
      temperature: {temperature}
      system_prompt: "You are {agent_role}"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                assert isinstance(spec, dict)
                assert spec["name"] == "{agent_name}"
                assert spec["components"][0]["config"]["agent_llm"] == "{llm_provider}"
                assert spec["components"][0]["config"]["model_name"] == "{model_name}"
                assert spec["components"][0]["config"]["temperature"] == "{temperature}"
                
            finally:
                os.unlink(f.name)

    def test_parse_specification_with_environment_variables(self, parser):
        """Test parsing specification with environment variables."""
        yaml_content = """
name: "Test Agent"
components:
  - id: "agent"
    type: "genesis:agent"
    config:
      api_key: "${OPENAI_API_KEY}"
      endpoint: "${API_ENDPOINT}"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                assert spec["components"][0]["config"]["api_key"] == "${OPENAI_API_KEY}"
                assert spec["components"][0]["config"]["endpoint"] == "${API_ENDPOINT}"
                
            finally:
                os.unlink(f.name)

    def test_parse_specification_with_complex_structure(self, parser):
        """Test parsing specification with complex nested structures."""
        yaml_content = """
name: "Complex Agent"
components:
  - id: "agent"
    type: "genesis:agent"
    config:
      nested:
        level1:
          level2:
            value: "deep"
            array: [1, 2, 3]
            object:
              key: "value"
      list_config:
        - item1: "value1"
          item2: "value2"
        - item3: "value3"
    provides:
      - useAs: "tool"
        in: "main-agent"
        metadata:
          priority: 1
          tags: ["important", "tool"]
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                # Verify complex structure is preserved
                agent_config = spec["components"][0]["config"]
                assert agent_config["nested"]["level1"]["level2"]["value"] == "deep"
                assert agent_config["nested"]["level1"]["level2"]["array"] == [1, 2, 3]
                assert agent_config["list_config"][0]["item1"] == "value1"
                assert spec["components"][0]["provides"][0]["metadata"]["tags"] == ["important", "tool"]
                
            finally:
                os.unlink(f.name)

    def test_parse_multi_agent_specification(self, parser):
        """Test parsing multi-agent specification."""
        yaml_content = """
id: "urn:agent:genesis:orchestrator:1"
name: "Multi-Agent Orchestrator"
fullyQualifiedName: "genesis.autonomize.ai.orchestrator"
description: "Orchestrator for multiple agents"
domain: "autonomize.ai"
subDomain: "orchestration"
version: "1.0.0"
environment: "production"
agentOwner: "orchestrator@example.com"
agentOwnerDisplayName: "Orchestrator Team"
email: "orchestrator@example.com"
status: "ACTIVE"

kind: "Multi Agent"
agentGoal: "Coordinate multiple agents"
targetUser: "internal"
valueGeneration: "ProcessAutomation"
interactionMode: "MultiTurnConversation"
runMode: "RealTime"
agencyLevel: "AdaptiveWorkflow"
toolsUse: true
learningCapability: "Contextual"

orchestration:
  type: "sequential"
  error_handling: "continue_on_error"
  timeout: 300
  flow:
    - step: "step1"
      agent: "agent1"
      inputs:
        data: "${input.data}"
      outputs:
        - result
    - step: "step2"
      agent: "agent2"
      inputs:
        data: "${step1.result}"
      outputs:
        - final_result

components:
  - id: "coordinator"
    type: "genesis:sequential_crew"
    config:
      workflow_name: "test_workflow"
      agents: ["agent1", "agent2"]
      
  - id: "agent1"
    type: "$ref:agent1"
    asTools: false
    
  - id: "agent2"
    type: "$ref:agent2"
    asTools: false

reusability:
  dependencies:
    - agentId: "urn:agent:genesis:agent1:1"
      version: ">=1.0.0"
      required: true
    - agentId: "urn:agent:genesis:agent2:1"
      version: ">=1.0.0"
      required: true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                assert isinstance(spec, AgentSpecV2Enhanced)
                assert spec.kind == "Multi Agent"
                assert spec.agencyLevel == AgencyLevel.ADAPTIVE_WORKFLOW
                assert "orchestration" in spec.model_extra
                assert spec.model_extra["orchestration"]["type"] == "sequential"
                assert len(spec.model_extra["orchestration"]["flow"]) == 2
                
            finally:
                os.unlink(f.name)

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_parse_specification_permission_error(self, mock_open, parser):
        """Test handling permission error when reading file."""
        with pytest.raises(PermissionError):
            parser.parse_specification("/some/file.yaml")

    def test_parse_specification_with_special_characters(self, parser):
        """Test parsing specification with special characters."""
        yaml_content = """
name: "Agent with Special Chars"
components:
  - id: "agent"
    type: "genesis:agent"
    config:
      system_prompt: |
        You are an agent that handles:
        - Special chars: @#$%^&*()
        - Unicode: 你好世界 🌍
        - Quotes: "double" and 'single'
        - Escape chars: \n \t \\
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                spec = parser.parse_specification(f.name)
                
                prompt = spec["components"][0]["config"]["system_prompt"]
                assert "@#$%^&*()" in prompt
                assert "你好世界 🌍" in prompt
                assert '"double"' in prompt
                assert "'single'" in prompt
                
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])