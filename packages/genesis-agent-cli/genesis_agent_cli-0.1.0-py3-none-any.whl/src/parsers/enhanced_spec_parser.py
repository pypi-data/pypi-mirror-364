"""
Enhanced Specification Parser - Parse both old and new specification formats.

This parser handles the complete specification format including all metadata
fields and multi-agent orchestration patterns.
"""

import yaml
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from src.models.agent_spec_enhanced import (
    AgentSpecV2Enhanced,
    AgentKind,
    TargetUser,
    ValueGeneration,
    InteractionMode,
    RunMode,
    AgencyLevel,
    LearningCapability,
    AgentStatus,
    Reusability,
    ReusabilityProvides,
    AgentDependency,
    KPI,
    OrchestrationConfig,
)


class EnhancedSpecParser:
    """
    Parser for enhanced agent specifications.

    This parser:
    - Handles the complete specification format with all metadata
    - Supports multi-agent orchestration patterns
    - Converts to simplified v2 format for flow generation
    - Maintains backward compatibility
    """

    def __init__(self):
        self._loaded_specs = {}  # Cache for loaded specifications

    def parse_specification(
        self, spec_path: str
    ) -> AgentSpecV2Enhanced:
        """
        Parse a YAML specification file.

        Automatically detects whether it's an enhanced format (with full metadata)
        or simplified v2 format.

        Args:
            spec_path: Path to the YAML specification file

        Returns:
            Parsed specification (enhanced or v2)
        """
        # Load YAML file
        spec_data = self._load_yaml(spec_path)

        # Detect format based on presence of key fields
        if self._is_enhanced_format(spec_data):
            return self._parse_enhanced(spec_data)
        else:
            # Use the regular v2 parser
            from src.parsers.spec_parser_v2 import SpecParserV2

            parser = SpecParserV2()
            return parser.parse_specification(spec_path)

    def _load_yaml(self, spec_path: str) -> Dict[str, Any]:
        """Load and parse YAML file."""
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("Specification must be a YAML dictionary")

        # Store path for reference resolution
        self._current_spec_dir = path.parent

        return data

    def _is_enhanced_format(self, spec_data: Dict[str, Any]) -> bool:
        """Check if specification is in enhanced format."""
        # Enhanced format has these fields at root level
        enhanced_fields = ["fullyQualifiedName", "agentGoal", "kind", "targetUser"]
        return any(field in spec_data for field in enhanced_fields)

    def _parse_enhanced(self, data: Dict[str, Any]) -> AgentSpecV2Enhanced:
        """Parse enhanced specification format."""
        # Substitute environment variables
        data = self._substitute_env_vars(data)

        # Parse reusability if present
        reusability = None
        if "reusability" in data:
            reusability = self._parse_reusability(data["reusability"])

        # Parse KPIs if present
        kpis = None
        if "kpis" in data:
            kpis = [KPI(**kpi) for kpi in data["kpis"]]

        # Parse orchestration specific config
        specific = None
        if "specific" in data:
            if data.get("kind") == "Orchestrator" and isinstance(
                data["specific"], dict
            ):
                specific = OrchestrationConfig(**data["specific"])
            else:
                specific = data["specific"]

        # Create enhanced specification
        spec = AgentSpecV2Enhanced(
            # Metadata
            id=data["id"],
            name=data["name"],
            fullyQualifiedName=data["fullyQualifiedName"],
            description=data["description"],
            domain=data["domain"],
            subDomain=data.get("subDomain"),
            version=data["version"],
            environment=data.get("environment", "production"),
            agentOwner=data["agentOwner"],
            agentOwnerDisplayName=data["agentOwnerDisplayName"],
            email=data["email"],
            status=data.get("status", "ACTIVE"),
            # Tags
            tags=data.get("tags", []),
            # Agent configuration
            kind=data["kind"],
            agentGoal=data["agentGoal"],
            targetUser=data["targetUser"],
            valueGeneration=data["valueGeneration"],
            interactionMode=data["interactionMode"],
            runMode=data["runMode"],
            agencyLevel=data["agencyLevel"],
            toolsUse=data.get("toolsUse", True),
            learningCapability=data.get("learningCapability", "None"),
            # Optional fields
            reusability=reusability,
            promptConfiguration=data.get("promptConfiguration"),
            knowledgeHub=data.get("knowledgeHub"),
            components=data.get("components", []),
            outputs=data.get("outputs"),
            kpis=kpis,
            securityInfo=data.get("securityInfo"),
            specific=specific,
            audit=data.get("audit"),
            config=data.get("config"),
        )

        return spec

    def _parse_reusability(self, data: Dict[str, Any]) -> Reusability:
        """Parse reusability configuration."""
        provides = None
        if "provides" in data:
            provides = ReusabilityProvides(**data["provides"])

        dependencies = []
        if "dependencies" in data:
            dependencies = [AgentDependency(**dep) for dep in data["dependencies"]]

        return Reusability(
            asTools=data.get("asTools", True),
            standalone=data.get("standalone", True),
            provides=provides,
            dependencies=dependencies,
        )

    def _substitute_env_vars(self, data: Any) -> Any:
        """Recursively substitute environment variables in data."""
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(v) for v in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            var_name = data[2:-1]
            return os.getenv(var_name, data)
        else:
            return data

    def convert_to_v2(self, enhanced_spec: AgentSpecV2Enhanced) -> Dict[str, Any]:
        """
        Convert enhanced specification to v2 format for flow generation.

        Args:
            enhanced_spec: Enhanced specification

        Returns:
            v2 format dictionary ready for flow generation
        """
        return enhanced_spec.to_v2_format()

    def parse_and_convert(self, spec_path: str) -> Dict[str, Any]:
        """
        Parse specification and convert to v2 format.

        This is a convenience method that handles both enhanced and
        regular v2 formats, always returning a v2 format dictionary.

        Args:
            spec_path: Path to specification file

        Returns:
            v2 format dictionary
        """
        spec = self.parse_specification(spec_path)

        if isinstance(spec, AgentSpecV2Enhanced):
            return self.convert_to_v2(spec)
        else:
            # Already in v2 format, convert to dict
            return spec.dict()

    def validate_enhanced_spec(self, spec: AgentSpecV2Enhanced) -> List[str]:
        """
        Validate an enhanced specification.

        Args:
            spec: Enhanced specification to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Required fields
        if not spec.id:
            errors.append("Missing required field: id")
        if not spec.name:
            errors.append("Missing required field: name")
        if not spec.agentGoal:
            errors.append("Missing required field: agentGoal")

        # Validate multi-agent dependencies
        if spec.reusability and spec.reusability.dependencies:
            for i, dep in enumerate(spec.reusability.dependencies):
                if not dep.agentId:
                    errors.append(f"Dependency {i}: missing agentId")

        # Validate components for agent references
        for i, component in enumerate(spec.components):
            if component.get("type", "").startswith("$ref:"):
                if not component.get("asTools"):
                    errors.append(
                        f"Component {i}: agent reference must have asTools: true"
                    )
                if "config" not in component or "tool_name" not in component["config"]:
                    errors.append(
                        f"Component {i}: agent reference must have tool_name in config"
                    )

        return errors
