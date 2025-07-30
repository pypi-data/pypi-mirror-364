"""
Unit tests for Agent Spec Enhanced models.
"""

import pytest
from pydantic import ValidationError

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
    Category,
    ComponentProvides
)


class TestAgentSpecEnhancedModels:
    """Test cases for Agent Spec Enhanced models."""

    def test_agency_level_enum(self):
        """Test AgencyLevel enum values."""
        assert AgencyLevel.STATIC_WORKFLOW == "StaticWorkflow"
        assert AgencyLevel.MODEL_DRIVEN_WORKFLOW == "ModelDrivenWorkflow"
        assert AgencyLevel.KNOWLEDGE_DRIVEN_WORKFLOW == "KnowledgeDrivenWorkflow"
        assert AgencyLevel.ADAPTIVE_WORKFLOW == "AdaptiveWorkflow"
        assert AgencyLevel.AUTONOMOUS == "Autonomous"

    def test_interaction_mode_enum(self):
        """Test InteractionMode enum values."""
        assert InteractionMode.REQUEST_RESPONSE == "RequestResponse"
        assert InteractionMode.MULTI_TURN_CONVERSATION == "MultiTurnConversation"
        assert InteractionMode.STREAMING == "Streaming"
        assert InteractionMode.BATCH == "Batch"

    def test_run_mode_enum(self):
        """Test RunMode enum values."""
        assert RunMode.REAL_TIME == "RealTime"
        assert RunMode.SCHEDULED == "Scheduled"
        assert RunMode.EVENT_DRIVEN == "EventDriven"

    def test_learning_capability_enum(self):
        """Test LearningCapability enum values."""
        assert LearningCapability.NONE == "None"
        assert LearningCapability.CONTEXTUAL == "Contextual"
        assert LearningCapability.PERSISTENT == "Persistent"
        assert LearningCapability.CONTINUOUS == "Continuous"

    def test_target_user_enum(self):
        """Test TargetUser enum values."""
        assert TargetUser.INTERNAL == "internal"
        assert TargetUser.EXTERNAL == "external"
        assert TargetUser.BOTH == "both"

    def test_value_generation_enum(self):
        """Test ValueGeneration enum values."""
        assert ValueGeneration.PROCESS_AUTOMATION == "ProcessAutomation"
        assert ValueGeneration.INSIGHT_GENERATION == "InsightGeneration"
        assert ValueGeneration.DECISION_SUPPORT == "DecisionSupport"
        assert ValueGeneration.CONTENT_CREATION == "ContentCreation"

    def test_status_enum(self):
        """Test Status enum values."""
        assert Status.ACTIVE == "ACTIVE"
        assert Status.INACTIVE == "INACTIVE"
        assert Status.DRAFT == "DRAFT"
        assert Status.ARCHIVED == "ARCHIVED"

    def test_value_type_enum(self):
        """Test ValueType enum values."""
        assert ValueType.NUMERIC == "numeric"
        assert ValueType.PERCENTAGE == "percentage"
        assert ValueType.BOOLEAN == "boolean"
        assert ValueType.STRING == "string"

    def test_category_enum(self):
        """Test Category enum values."""
        assert Category.QUALITY == "Quality"
        assert Category.PERFORMANCE == "Performance"
        assert Category.EFFICIENCY == "Efficiency"
        assert Category.RELIABILITY == "Reliability"

    def test_kpi_model_valid(self):
        """Test valid KPI model creation."""
        kpi = KPI(
            name="Success Rate",
            category=Category.QUALITY,
            valueType=ValueType.PERCENTAGE,
            target=98.5,
            unit="%",
            description="Percentage of successful operations"
        )
        
        assert kpi.name == "Success Rate"
        assert kpi.category == Category.QUALITY
        assert kpi.valueType == ValueType.PERCENTAGE
        assert kpi.target == 98.5
        assert kpi.unit == "%"
        assert kpi.description == "Percentage of successful operations"

    def test_kpi_model_minimal(self):
        """Test KPI model with minimal required fields."""
        kpi = KPI(
            name="Test KPI",
            category=Category.PERFORMANCE,
            valueType=ValueType.NUMERIC,
            target=100
        )
        
        assert kpi.name == "Test KPI"
        assert kpi.category == Category.PERFORMANCE
        assert kpi.valueType == ValueType.NUMERIC
        assert kpi.target == 100
        assert kpi.unit is None
        assert kpi.description is None

    def test_kpi_model_invalid_category(self):
        """Test KPI model with invalid category."""
        with pytest.raises(ValidationError) as exc_info:
            KPI(
                name="Test KPI",
                category="InvalidCategory",
                valueType=ValueType.NUMERIC,
                target=100
            )
        
        errors = exc_info.value.errors()
        assert any("not a valid enumeration member" in str(error) for error in errors)

    def test_component_provides_model(self):
        """Test ComponentProvides model."""
        provides = ComponentProvides(
            useAs="input",
            in_="target-component",
            description="Connect input to target"
        )
        
        assert provides.useAs == "input"
        assert provides.in_ == "target-component"
        assert provides.description == "Connect input to target"

    def test_component_provides_minimal(self):
        """Test ComponentProvides with minimal fields."""
        provides = ComponentProvides(
            useAs="output",
            in_="next-component"
        )
        
        assert provides.useAs == "output"
        assert provides.in_ == "next-component"
        assert provides.description is None

    def test_agent_spec_v2_enhanced_valid(self):
        """Test valid AgentSpecV2Enhanced creation."""
        spec = AgentSpecV2Enhanced(
            id="urn:agent:genesis:test:1",
            name="Test Agent",
            fullyQualifiedName="genesis.autonomize.ai.test",
            description="Test agent description",
            domain="autonomize.ai",
            subDomain="testing",
            version="1.0.0",
            environment="production",
            agentOwner="test@example.com",
            agentOwnerDisplayName="Test Team",
            email="test@example.com",
            status=Status.ACTIVE,
            kind="Single Agent",
            agentGoal="Perform test operations",
            targetUser=TargetUser.INTERNAL,
            valueGeneration=ValueGeneration.PROCESS_AUTOMATION,
            interactionMode=InteractionMode.REQUEST_RESPONSE,
            runMode=RunMode.REAL_TIME,
            agencyLevel=AgencyLevel.MODEL_DRIVEN_WORKFLOW,
            toolsUse=True,
            learningCapability=LearningCapability.NONE,
            components=[
                {
                    "id": "input",
                    "name": "Input",
                    "type": "genesis:chat_input"
                }
            ]
        )
        
        assert spec.id == "urn:agent:genesis:test:1"
        assert spec.name == "Test Agent"
        assert spec.agentGoal == "Perform test operations"
        assert spec.agencyLevel == AgencyLevel.MODEL_DRIVEN_WORKFLOW
        assert spec.toolsUse is True
        assert len(spec.components) == 1

    def test_agent_spec_v2_enhanced_with_optional_fields(self):
        """Test AgentSpecV2Enhanced with optional fields."""
        spec = AgentSpecV2Enhanced(
            id="test-id",
            name="Test",
            fullyQualifiedName="test.fqn",
            description="Test",
            domain="test",
            subDomain="test",
            version="1.0.0",
            environment="test",
            agentOwner="test@test.com",
            agentOwnerDisplayName="Test",
            email="test@test.com",
            status=Status.ACTIVE,
            kind="Single Agent",
            agentGoal="Test goal",
            targetUser=TargetUser.INTERNAL,
            valueGeneration=ValueGeneration.PROCESS_AUTOMATION,
            interactionMode=InteractionMode.REQUEST_RESPONSE,
            runMode=RunMode.REAL_TIME,
            agencyLevel=AgencyLevel.MODEL_DRIVEN_WORKFLOW,
            toolsUse=False,
            learningCapability=LearningCapability.NONE,
            components=[],
            # Optional fields
            tags=["test", "unit-test"],
            kpis=[
                KPI(
                    name="Test KPI",
                    category=Category.QUALITY,
                    valueType=ValueType.PERCENTAGE,
                    target=95
                )
            ],
            reusability={
                "asTools": True,
                "standalone": False,
                "provides": {
                    "toolName": "TestTool",
                    "toolDescription": "Test tool"
                }
            },
            sampleInput={"key": "value"},
            outputs=["result"],
            securityInfo={
                "visibility": "Private",
                "confidentiality": "High",
                "gdprSensitive": True
            }
        )
        
        assert spec.tags == ["test", "unit-test"]
        assert len(spec.kpis) == 1
        assert spec.kpis[0].name == "Test KPI"
        assert spec.reusability["asTools"] is True
        assert spec.sampleInput == {"key": "value"}
        assert spec.outputs == ["result"]
        assert spec.securityInfo["gdprSensitive"] is True

    def test_agent_spec_v2_enhanced_invalid_agency_level(self):
        """Test AgentSpecV2Enhanced with invalid agency level."""
        with pytest.raises(ValidationError) as exc_info:
            AgentSpecV2Enhanced(
                id="test-id",
                name="Test",
                fullyQualifiedName="test.fqn",
                description="Test",
                domain="test",
                subDomain="test",
                version="1.0.0",
                environment="test",
                agentOwner="test@test.com",
                agentOwnerDisplayName="Test",
                email="test@test.com",
                status=Status.ACTIVE,
                kind="Single Agent",
                agentGoal="Test goal",
                targetUser=TargetUser.INTERNAL,
                valueGeneration=ValueGeneration.PROCESS_AUTOMATION,
                interactionMode=InteractionMode.REQUEST_RESPONSE,
                runMode=RunMode.REAL_TIME,
                agencyLevel="InvalidLevel",  # Invalid
                toolsUse=False,
                learningCapability=LearningCapability.NONE,
                components=[]
            )
        
        errors = exc_info.value.errors()
        assert any("not a valid enumeration member" in str(error) for error in errors)

    def test_agent_spec_v2_enhanced_missing_required_field(self):
        """Test AgentSpecV2Enhanced with missing required field."""
        with pytest.raises(ValidationError) as exc_info:
            AgentSpecV2Enhanced(
                id="test-id",
                name="Test",
                # Missing fullyQualifiedName and other required fields
            )
        
        errors = exc_info.value.errors()
        assert any("field required" in str(error) for error in errors)

    def test_agent_spec_v2_enhanced_extra_fields(self):
        """Test AgentSpecV2Enhanced with extra fields."""
        spec = AgentSpecV2Enhanced(
            id="test-id",
            name="Test",
            fullyQualifiedName="test.fqn",
            description="Test",
            domain="test",
            subDomain="test",
            version="1.0.0",
            environment="test",
            agentOwner="test@test.com",
            agentOwnerDisplayName="Test",
            email="test@test.com",
            status=Status.ACTIVE,
            kind="Single Agent",
            agentGoal="Test goal",
            targetUser=TargetUser.INTERNAL,
            valueGeneration=ValueGeneration.PROCESS_AUTOMATION,
            interactionMode=InteractionMode.REQUEST_RESPONSE,
            runMode=RunMode.REAL_TIME,
            agencyLevel=AgencyLevel.MODEL_DRIVEN_WORKFLOW,
            toolsUse=False,
            learningCapability=LearningCapability.NONE,
            components=[],
            # Extra fields
            orchestration={
                "type": "sequential",
                "timeout": 300
            },
            customField="custom value"
        )
        
        # Extra fields should be stored in model_extra
        assert "orchestration" in spec.model_extra
        assert spec.model_extra["orchestration"]["type"] == "sequential"
        assert "customField" in spec.model_extra
        assert spec.model_extra["customField"] == "custom value"

    def test_agent_spec_v2_enhanced_with_prompt_configuration(self):
        """Test AgentSpecV2Enhanced with promptConfiguration."""
        spec = AgentSpecV2Enhanced(
            id="test-id",
            name="Test",
            fullyQualifiedName="test.fqn",
            description="Test",
            domain="test",
            subDomain="test",
            version="1.0.0",
            environment="test",
            agentOwner="test@test.com",
            agentOwnerDisplayName="Test",
            email="test@test.com",
            status=Status.ACTIVE,
            kind="Single Agent",
            agentGoal="Test goal",
            targetUser=TargetUser.INTERNAL,
            valueGeneration=ValueGeneration.PROCESS_AUTOMATION,
            interactionMode=InteractionMode.REQUEST_RESPONSE,
            runMode=RunMode.REAL_TIME,
            agencyLevel=AgencyLevel.MODEL_DRIVEN_WORKFLOW,
            toolsUse=False,
            learningCapability=LearningCapability.NONE,
            components=[],
            promptConfiguration={
                "basePromptId": "test_prompt_v1",
                "customPrompt": "You are a test agent"
            }
        )
        
        assert "promptConfiguration" in spec.model_extra
        assert spec.model_extra["promptConfiguration"]["basePromptId"] == "test_prompt_v1"

    def test_agent_spec_v2_enhanced_with_variables(self):
        """Test AgentSpecV2Enhanced with variables."""
        spec = AgentSpecV2Enhanced(
            id="test-id",
            name="Test",
            fullyQualifiedName="test.fqn",
            description="Test",
            domain="test",
            subDomain="test",
            version="1.0.0",
            environment="test",
            agentOwner="test@test.com",
            agentOwnerDisplayName="Test",
            email="test@test.com",
            status=Status.ACTIVE,
            kind="Single Agent",
            agentGoal="Test goal",
            targetUser=TargetUser.INTERNAL,
            valueGeneration=ValueGeneration.PROCESS_AUTOMATION,
            interactionMode=InteractionMode.REQUEST_RESPONSE,
            runMode=RunMode.REAL_TIME,
            agencyLevel=AgencyLevel.MODEL_DRIVEN_WORKFLOW,
            toolsUse=False,
            learningCapability=LearningCapability.NONE,
            components=[],
            variables=[
                {
                    "name": "temperature",
                    "type": "float",
                    "required": False,
                    "default": 0.7,
                    "description": "Temperature for LLM"
                }
            ]
        )
        
        assert "variables" in spec.model_extra
        assert len(spec.model_extra["variables"]) == 1
        assert spec.model_extra["variables"][0]["name"] == "temperature"

    def test_component_provides_dict_method(self):
        """Test ComponentProvides dict method."""
        provides = ComponentProvides(
            useAs="input",
            in_="target",
            description="Test description"
        )
        
        provides_dict = provides.dict()
        
        assert provides_dict["useAs"] == "input"
        assert provides_dict["in"] == "target"
        assert provides_dict["description"] == "Test description"

    def test_kpi_model_numeric_validation(self):
        """Test KPI model numeric validation."""
        # Test with negative target (should be allowed)
        kpi = KPI(
            name="Test KPI",
            category=Category.PERFORMANCE,
            valueType=ValueType.NUMERIC,
            target=-10.5
        )
        assert kpi.target == -10.5
        
        # Test with zero target
        kpi = KPI(
            name="Test KPI",
            category=Category.PERFORMANCE,
            valueType=ValueType.PERCENTAGE,
            target=0
        )
        assert kpi.target == 0
        
        # Test with very large target
        kpi = KPI(
            name="Test KPI",
            category=Category.PERFORMANCE,
            valueType=ValueType.NUMERIC,
            target=1e10
        )
        assert kpi.target == 1e10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])