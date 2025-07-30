"""
Enhanced Agent Specification v2 Models - Complete format with all metadata.

This module defines the enhanced v2 specification format that includes
all metadata fields and multi-agent orchestration support.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums for agent configuration
class AgentKind(str, Enum):
    """Agent kind/type."""

    SINGLE_AGENT = "Single Agent"
    MULTI_AGENT = "Multi Agent"
    ORCHESTRATOR = "Orchestrator"


class TargetUser(str, Enum):
    """Target user type."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    BOTH = "both"


class ValueGeneration(str, Enum):
    """Value generation type."""

    PROCESS_AUTOMATION = "ProcessAutomation"
    INSIGHT_GENERATION = "InsightGeneration"
    DECISION_SUPPORT = "DecisionSupport"
    CONTENT_CREATION = "ContentCreation"


class InteractionMode(str, Enum):
    """Interaction mode."""

    REQUEST_RESPONSE = "RequestResponse"
    MULTI_TURN_CONVERSATION = "MultiTurnConversation"
    STREAMING = "Streaming"
    BATCH = "Batch"


class RunMode(str, Enum):
    """Run mode."""

    REAL_TIME = "RealTime"
    SCHEDULED = "Scheduled"
    EVENT_DRIVEN = "EventDriven"


class AgencyLevel(str, Enum):
    """Agency level."""

    STATIC_WORKFLOW = "StaticWorkflow"
    MODEL_DRIVEN_WORKFLOW = "ModelDrivenWorkflow"
    KNOWLEDGE_DRIVEN_WORKFLOW = "KnowledgeDrivenWorkflow"
    ADAPTIVE_WORKFLOW = "AdaptiveWorkflow"
    AUTONOMOUS = "Autonomous"


class LearningCapability(str, Enum):
    """Learning capability."""

    NONE = "None"
    CONTEXTUAL = "Contextual"
    PERSISTENT = "Persistent"
    CONTINUOUS = "Continuous"


class AgentStatus(str, Enum):
    """Agent status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    TESTING = "TESTING"


# Reusability models
class ReusabilityProvides(BaseModel):
    """What this agent provides when used as a tool."""

    toolName: str = Field(..., description="Name when used as tool")
    toolDescription: str = Field(..., description="Description when used as tool")
    inputSchema: Dict[str, Any] = Field(..., description="Expected input schema")
    outputSchema: Dict[str, Any] = Field(..., description="Output schema")


class AgentDependency(BaseModel):
    """Agent dependency specification."""

    agentId: str = Field(..., description="Agent ID to depend on")
    version: str = Field(">=1.0.0", description="Version constraint")
    required: bool = Field(True, description="Whether dependency is required")


class Reusability(BaseModel):
    """Agent reusability configuration."""

    asTools: bool = Field(True, description="Can be used as tool by other agents")
    standalone: bool = Field(True, description="Can run independently")
    provides: Optional[ReusabilityProvides] = None
    dependencies: Optional[List[AgentDependency]] = Field(default_factory=list)


# Enhanced metadata
class EnhancedMetadata(BaseModel):
    """Enhanced agent metadata with all fields."""

    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    fullyQualifiedName: str = Field(..., description="Fully qualified name")
    description: str = Field(..., description="Agent description")
    domain: str = Field(..., description="Domain (e.g., autonomize.ai)")
    subDomain: Optional[str] = Field(None, description="Sub-domain")
    version: str = Field(..., description="Agent version")
    environment: str = Field("production", description="Environment")
    agentOwner: str = Field(..., description="Agent owner email")
    agentOwnerDisplayName: str = Field(..., description="Owner display name")
    email: str = Field(..., description="Contact email")
    status: AgentStatus = Field(AgentStatus.ACTIVE, description="Agent status")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


# Agent configuration
class AgentConfiguration(BaseModel):
    """Complete agent configuration."""

    kind: AgentKind = Field(..., description="Agent kind")
    agentGoal: str = Field(..., description="Primary goal of the agent")
    targetUser: TargetUser = Field(..., description="Target user type")
    valueGeneration: ValueGeneration = Field(..., description="Value generation type")
    interactionMode: InteractionMode = Field(..., description="Interaction mode")
    runMode: RunMode = Field(..., description="Run mode")
    agencyLevel: AgencyLevel = Field(..., description="Agency level")
    toolsUse: bool = Field(True, description="Whether agent uses tools")
    learningCapability: LearningCapability = Field(LearningCapability.NONE)


# KPIs and metrics
class KPI(BaseModel):
    """Key Performance Indicator."""

    name: str = Field(..., description="KPI name")
    description: str = Field(..., description="KPI description")
    target: Optional[Union[str, float, int]] = Field(None, description="Target value")
    unit: Optional[str] = Field(None, description="Unit of measurement")


# Tool configuration for agents as tools
class AgentAsToolConfig(BaseModel):
    """Configuration for using an agent as a tool."""

    type: str = Field(..., description="Should be '$ref:agent_id' format")
    id: str = Field(..., description="Tool instance ID")
    name: str = Field(..., description="Tool display name")
    description: str = Field(..., description="Tool description")
    asTools: bool = Field(True, description="Must be True for agent tools")
    config: Dict[str, Any] = Field(default_factory=dict)


# Orchestration specific config
class OrchestrationConfig(BaseModel):
    """Configuration specific to orchestrator agents."""

    orchestrationStrategy: str = Field(
        "sequential", description="Orchestration strategy"
    )
    agentTimeout: int = Field(60, description="Timeout per agent in seconds")
    fallbackBehavior: str = Field("continue", description="Behavior on failure")
    aggregateResults: bool = Field(True, description="Whether to aggregate results")
    errorHandling: str = Field("graceful", description="Error handling strategy")


# Main specification
class AgentSpecV2Enhanced(BaseModel):
    """
    Enhanced Agent Specification v2 with complete metadata.

    This specification includes all fields from the original format
    plus support for multi-agent orchestration.
    """

    # Metadata
    id: str
    name: str
    fullyQualifiedName: str
    description: str
    domain: str
    subDomain: Optional[str] = None
    version: str
    environment: str = "production"
    agentOwner: str
    agentOwnerDisplayName: str
    email: str
    status: AgentStatus = AgentStatus.ACTIVE

    # Tags
    tags: List[str] = Field(default_factory=list)

    # Agent configuration
    kind: AgentKind
    agentGoal: str
    targetUser: TargetUser
    valueGeneration: ValueGeneration
    interactionMode: InteractionMode
    runMode: RunMode
    agencyLevel: AgencyLevel
    toolsUse: bool = True
    learningCapability: LearningCapability = LearningCapability.NONE

    # Reusability (for multi-agent)
    reusability: Optional[Reusability] = None

    # Prompt configuration
    promptConfiguration: Optional[Dict[str, Any]] = None

    # Knowledge Hub
    knowledgeHub: Optional[Dict[str, Any]] = None

    # Components (tools, agents, etc.)
    components: List[Dict[str, Any]] = Field(default_factory=list)

    # Outputs
    outputs: Optional[List[str]] = None

    # KPIs
    kpis: Optional[List[KPI]] = None

    # Security
    securityInfo: Optional[Dict[str, Any]] = None

    # Orchestration specific
    specific: Optional[Union[OrchestrationConfig, Dict[str, Any]]] = None

    # Audit
    audit: Optional[Dict[str, Any]] = None

    # Config
    config: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True

    def to_v2_format(self) -> Dict[str, Any]:
        """Convert to simplified v2 format for flow generation."""
        # Extract agent configuration
        agent_config = {
            "agent_llm": "Azure OpenAI",  # Default, can be overridden
            "model_name": "gpt-4",  # Default
            "system_prompt": self.agentGoal,
            "temperature": 0.1 if self.valueGeneration == "ProcessAutomation" else 0.7,
            "max_iterations": 15 if self.kind == "Orchestrator" else 10,
            "verbose": True,
        }

        # Build v2 format
        v2_spec = {
            "version": "2.0",
            "metadata": {
                "id": self.id,
                "name": self.name,
                "version": self.version,
                "domain": self.domain,
                "owner": self.agentOwner,
            },
            "agent": {"type": "genesis:autonomize_agent", "config": agent_config},
        }

        # Add prompts if configured
        if self.promptConfiguration:
            if "basePromptId" in self.promptConfiguration:
                v2_spec["prompts"] = {
                    "saved": {
                        "name": self.promptConfiguration["basePromptId"],
                        "variables": self.promptConfiguration.get("variables", {}),
                    }
                }
            elif "customPrompt" in self.promptConfiguration:
                v2_spec["prompts"] = {
                    "inline": {"template": self.promptConfiguration["customPrompt"]}
                }

        # Add knowledge hubs
        if self.knowledgeHub and "collections" in self.knowledgeHub:
            v2_spec["knowledge"] = {
                "hubs": [c["name"] for c in self.knowledgeHub["collections"]]
            }

        # Process components to tools
        tools = []
        outputs = []

        for component in self.components:
            comp_type = component.get("type", "")

            # Handle agent references (multi-agent pattern)
            if comp_type.startswith("$ref:"):
                agent_ref = {
                    "type": "genesis:agent_tool",
                    "id": component["id"],
                    "config": {
                        "agent_id": comp_type.replace("$ref:", ""),
                        "tool_name": component.get("config", {}).get(
                            "tool_name", component["name"]
                        ),
                        "tool_description": component.get("config", {}).get(
                            "tool_description", component["description"]
                        ),
                    },
                }
                tools.append(agent_ref)
            # Handle outputs
            elif "output" in comp_type.lower() or "formatter" in comp_type.lower():
                output = {
                    "type": (
                        f"genesis:{component['type']}"
                        if not component["type"].startswith("genesis:")
                        else component["type"]
                    ),
                    "id": component["id"],
                    "config": component.get("config", {}),
                }
                outputs.append(output)
            # Handle regular tools
            elif component.get("asTools", False):
                tool = {
                    "type": (
                        f"genesis:{component['type']}"
                        if not component["type"].startswith("genesis:")
                        else component["type"]
                    ),
                    "id": component["id"],
                    "config": component.get("config", {}),
                }
                tools.append(tool)

        if tools:
            v2_spec["tools"] = tools
        if outputs:
            v2_spec["outputs"] = outputs

        # Add security if present
        if self.securityInfo:
            v2_spec["security"] = self.securityInfo

        return v2_spec
