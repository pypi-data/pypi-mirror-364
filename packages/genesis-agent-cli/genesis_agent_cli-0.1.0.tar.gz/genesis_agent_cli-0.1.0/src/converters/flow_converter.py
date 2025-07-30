"""
Genesis Flow Converter - Converts agent specifications to Genesis Studio flows.

This converter:
1. Validates components against Genesis Studio
2. Maps Genesis types to Langflow components
3. Creates connections using the provides pattern
4. Generates valid Langflow JSON with proper edge encoding
"""

import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid

from src.models.agent_spec_enhanced import AgentSpecV2Enhanced
from src.models.component_provides import ComponentProvides
from src.parsers.enhanced_spec_parser import EnhancedSpecParser
from src.services.component_loader import ComponentLoader, ComponentValidator
from src.services.config import Config
from src.services.variable_resolver import VariableResolver
from src.registry.dynamic_component_mapper import get_dynamic_mapper, get_langflow_component_type


class FlowConverter:
    """Converts agent specifications to Genesis Studio flows."""
    
    def __init__(self, config: Config, variable_resolver: Optional[VariableResolver] = None):
        """Initialize the flow converter.
        
        Args:
            config: Configuration for API access
            variable_resolver: Optional variable resolver for runtime variables
        """
        self.config = config
        self.parser = EnhancedSpecParser()
        self.component_loader = ComponentLoader(config)
        self.component_validator = ComponentValidator(self.component_loader)
        self.dynamic_mapper = None  # Will be loaded asynchronously
        self.variable_resolver = variable_resolver or VariableResolver()
        
    async def convert(self, spec_path: str) -> Dict[str, Any]:
        """Convert a specification file to Genesis Studio flow.
        
        Args:
            spec_path: Path to the specification YAML file
            
        Returns:
            Complete flow structure for Genesis Studio
        """
        # Initialize dynamic mapper if not already done
        if not self.dynamic_mapper:
            self.dynamic_mapper = await get_dynamic_mapper(self.config)
            
        # Parse specification
        spec = self.parser.parse_specification(spec_path)
        
        # Validate components
        validation_result = await self.component_validator.validate_spec(spec)
        
        if not validation_result["valid"]:
            print("\n⚠️  Component validation issues:")
            for error in validation_result["errors"]:
                print(f"   ❌ {error}")
            for warning in validation_result["warnings"]:
                print(f"   ⚠️  {warning}")
                
            if validation_result["missing_components"]:
                print(f"\n   Missing components will be filtered out: {', '.join(validation_result['missing_components'])}")
                spec = self._filter_invalid_components(spec, validation_result["missing_components"])
        
        # Build flow
        nodes = await self._build_nodes(spec)
        edges = await self._build_edges(spec, nodes)
        
        # Create flow structure
        flow = {
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.5}
            },
            "name": spec.name if hasattr(spec, "name") else "Untitled Flow",
            "description": spec.description if hasattr(spec, "description") else "",
            "is_component": False,
            "updated_at": datetime.utcnow().isoformat(),
            "folder": None,
            "id": None,
            "user_id": None,
            "webhook": False,
            "endpoint_name": None
        }
        
        # Add metadata for enhanced specs
        if isinstance(spec, AgentSpecV2Enhanced):
            flow["metadata"] = {
                "agentGoal": spec.agentGoal,
                "targetUser": spec.targetUser,
                "valueGeneration": spec.valueGeneration,
                "kind": spec.kind,
                "tags": spec.tags,
                "kpis": [kpi.dict() for kpi in spec.kpis] if spec.kpis else []
            }
            
        return flow
    
    async def _build_nodes(self, spec: Any) -> List[Dict[str, Any]]:
        """Build nodes from specification components."""
        nodes = []
        
        # Extract components
        components = []
        if hasattr(spec, "components"):
            components = spec.components
        elif isinstance(spec, dict) and "components" in spec:
            components = spec["components"]
            
        # Build each component as a node
        for i, component in enumerate(components):
            node = await self._build_node(component, i, spec)
            if node:
                nodes.append(node)
                
        return nodes
    
    async def _build_node(self, component: Dict[str, Any], index: int, spec: Any = None) -> Optional[Dict[str, Any]]:
        """Build a single node from component specification."""
        # Get component info
        comp_id = component.get("id", f"node-{uuid.uuid4().hex[:8]}")
        comp_type = component.get("type", "")
        comp_name = component.get("name", comp_id)
        comp_description = component.get("description", "")
        
        # Map Genesis type to actual Genesis Studio component type
        if self.dynamic_mapper:
            langflow_type = self.dynamic_mapper.get_component_type(comp_type)
        else:
            langflow_type = get_langflow_component_type(comp_type)
        
        # Get raw component data from dynamic mapper
        comp_data = None
        if hasattr(self.dynamic_mapper, '_components_cache') and self.dynamic_mapper._components_cache:
            # Find the component in the cache
            for category, components in self.dynamic_mapper._components_cache.items():
                if isinstance(components, dict) and langflow_type in components:
                    comp_data = components[langflow_type]
                    break
        
        if not comp_data:
            print(f"⚠️  Component '{langflow_type}' not found in Genesis Studio, skipping")
            return None
        
        # Get category from the component's location in cache
        category = "custom"
        for cat, components in self.dynamic_mapper._components_cache.items():
            if isinstance(components, dict) and langflow_type in components:
                category = cat
                break
                
        # Calculate position
        position = self._calculate_position(index, category)
        
        # Check if this component is used as a tool
        is_tool = self._is_component_used_as_tool(component)
        
        # Deep copy component data to avoid modifying the cached version
        import copy
        node_data = copy.deepcopy(comp_data)
        
        # Handle tool mode
        if is_tool:
            # Set tool mode
            node_data["tool_mode"] = True
            
            # Ensure we have the component_as_tool output
            if "outputs" in node_data:
                # Check if component_as_tool already exists
                has_tool_output = any(o.get("name") == "component_as_tool" for o in node_data["outputs"])
                
                if not has_tool_output:
                    # Add component_as_tool output
                    node_data["outputs"] = [{
                        "types": ["Tool"],
                        "selected": "Tool",
                        "name": "component_as_tool",
                        "display_name": "Toolset",
                        "method": "to_toolkit",
                        "value": "__UNDEFINED__",
                        "cache": True,
                        "allows_loop": False,
                        "tool_mode": True
                    }]
        
        # Build node structure using component data
        node = {
            "id": comp_id,
            "type": "genericNode",
            "position": position,
            "data": {
                "id": comp_id,
                "type": langflow_type,  # Use actual component type name
                "description": comp_description or node_data.get("description", ""),
                "display_name": comp_name,
                "node": node_data,  # Use the modified component data
                "outputs": node_data.get("outputs", [])
            },
            "dragging": False,
            "height": self._get_node_height(category),
            "selected": False,
            "positionAbsolute": position,
            "width": 384
        }
        
        # Update template with component config
        if "template" in node["data"]["node"] and component.get("config"):
            self._apply_config_to_template(
                node["data"]["node"]["template"], 
                component["config"], 
                component=component,
                spec=spec
            )
        
        return node
    
    def _apply_config_to_template(self, template: Dict[str, Any], config: Dict[str, Any], 
                                   component: Dict[str, Any] = None, spec: Any = None):
        """Apply component config values to the template.
        
        Args:
            template: The node template to update
            config: Configuration values to apply
            component: The component specification (optional)
            spec: The full agent specification (optional)
        """
        # Special handling for Agent components
        if component and component.get("type") == "genesis:agent":
            # Always use agentGoal as system_prompt if available
            if "system_prompt" not in config and hasattr(spec, 'agentGoal') and spec.agentGoal:
                config = dict(config)  # Create a copy to avoid modifying original
                config["system_prompt"] = spec.agentGoal
                print(f"📝 Using agentGoal as system_prompt: {spec.agentGoal[:50]}...")
        
        # Resolve variables in config values
        resolved_config = self.variable_resolver.resolve(config)
        
        for key, value in resolved_config.items():
            if key in template and isinstance(template[key], dict):
                # Check if this is still a variable reference after resolution
                if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                    # This is an unresolved variable reference, keep it for Langflow to resolve
                    template[key]["value"] = value
                    print(f"🔗 Keeping variable reference for {key}: {value}")
                else:
                    template[key]["value"] = value
    
    
    async def _build_edges(self, spec: Any, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build edges from provides declarations."""
        edges = []
        node_map = {node["id"]: node for node in nodes}
        
        # Extract components with provides
        components = []
        if hasattr(spec, "components"):
            components = spec.components
        elif isinstance(spec, dict) and "components" in spec:
            components = spec["components"]
            
        # Process each component's provides declarations
        for component in components:
            if "provides" not in component or not component["provides"]:
                continue
                
            source_id = component.get("id")
            if source_id not in node_map:
                print(f"⚠️  Source node '{source_id}' not found in node map")
                continue
                
            print(f"🔍 Processing provides for component: {source_id} ({component.get('type')})")
            
            # Process each provides declaration
            for provide in component["provides"]:
                print(f"  → Provides: useAs={provide.get('useAs')}, in={provide.get('in')}")
                edge = self._create_edge_from_provides(
                    source_id, 
                    provide, 
                    node_map,
                    component
                )
                if edge:
                    edges.append(edge)
                    print(f"  ✅ Edge created: {source_id} → {provide.get('in')}")
                else:
                    print(f"  ❌ Edge creation failed")
                    
        return edges
    
    def _create_edge_from_provides(
        self, 
        source_id: str, 
        provide: Dict[str, Any], 
        node_map: Dict[str, Dict[str, Any]],
        source_component: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create an edge from a provides declaration."""
        # Get target info
        target_id = provide.get("in")
        use_as = provide.get("useAs")
        
        if not target_id or not use_as:
            return None
            
        if target_id not in node_map:
            print(f"⚠️  Target node '{target_id}' not found for provides connection")
            return None
            
        # Get nodes
        source_node = node_map[source_id]
        target_node = node_map[target_id]
        
        # Get actual component types
        source_type = source_node["data"]["type"]
        target_type = target_node["data"]["type"]
        
        # Determine output field based on useAs and component outputs
        output_field = self._determine_output_field(use_as, source_node, source_type)
        
        # Determine input field
        input_field = self._map_use_as_to_field(use_as)
        
        # Determine output types based on the output field
        output_types = self._get_output_types(source_node, output_field)
        
        # Create handle objects
        source_handle = {
            "dataType": source_type,  # Use actual component type
            "id": source_id,
            "name": output_field,
            "output_types": output_types
        }
        
        # Determine input types based on the field
        input_types = self._get_input_types(target_node, input_field)
        
        # Validate type compatibility
        if not self._validate_type_compatibility(output_types, input_types, source_type, target_type):
            print(f"⚠️  Type mismatch: {source_type} outputs {output_types} but {target_type}.{input_field} expects {input_types}")
            print(f"   Consider using a different output component that accepts {output_types[0] if output_types else 'the output type'}")
            return None
        
        # Determine handle type based on Genesis Studio conventions
        handle_type = self._determine_handle_type(input_field, input_types)
        
        target_handle = {
            "fieldName": input_field,
            "id": target_id,
            "inputTypes": input_types,
            "type": handle_type
        }
        
        # Encode handles
        source_handle_encoded = json.dumps(source_handle, separators=(",", ":")).replace('"', "œ")
        target_handle_encoded = json.dumps(target_handle, separators=(",", ":")).replace('"', "œ")
        
        # Create edge
        edge = {
            "className": "",
            "data": {
                "sourceHandle": source_handle,
                "targetHandle": target_handle,
                "label": provide.get("description", "")
            },
            "id": f"reactflow__edge-{source_id}{source_handle_encoded}-{target_id}{target_handle_encoded}",
            "selected": False,
            "source": source_id,
            "sourceHandle": source_handle_encoded,
            "target": target_id,
            "targetHandle": target_handle_encoded
        }
        
        return edge
    
    def _determine_output_field(self, use_as: str, source_node: Dict[str, Any], source_type: str) -> str:
        """Determine the output field based on useAs type and component."""
        # Special case for tools - they use component_as_tool
        if use_as in ["tool", "tools"]:
            return "component_as_tool"
            
        # Check if node has outputs defined
        outputs = source_node.get("data", {}).get("outputs", [])
        if outputs:
            # For agents, typically use "response"
            if "Agent" in source_type and any(o.get("name") == "response" for o in outputs):
                return "response"
            # For prompts, typically use "prompt"
            elif "Prompt" in source_type and any(o.get("name") == "prompt" for o in outputs):
                return "prompt"
            # Otherwise use first output
            return outputs[0].get("name", "output")
            
        # Default mappings
        output_mappings = {
            "input": "message",
            "tool": "component_as_tool",
            "tools": "component_as_tool",
            "system_prompt": "prompt",
            "prompt": "prompt",
            "llm": "text_output",
            "response": "response",
            "message": "message",
            "text": "text",
            "output": "output"
        }
        
        return output_mappings.get(use_as, "output")
    
    def _map_use_as_to_field(self, use_as: str) -> str:
        """Map useAs value to Langflow field name."""
        field_mappings = {
            "input": "input_value",
            "tool": "tools",
            "tools": "tools",
            "system_prompt": "system_prompt",  # Agent uses system_prompt field
            "prompt": "system_prompt",  # Map prompt to system_prompt for agents
            "llm": "llm",
            "response": "input_value",
            "message": "message",
            "text": "text",
            "output": "input_value"
        }
        
        return field_mappings.get(use_as, use_as)
    
    def _calculate_position(self, index: int, category: str) -> Dict[str, int]:
        """Calculate node position based on index and category."""
        # Base positions for categories
        category_positions = {
            "agents": {"x": 400, "y": 200},
            "prompts": {"x": 200, "y": 50},
            "tools": {"x": 200, "y": 350},
            "models": {"x": 200, "y": 350},
            "llms": {"x": 200, "y": 100},
            "outputs": {"x": 600, "y": 200},
            "inputs": {"x": 50, "y": 200}
        }
        
        base_pos = category_positions.get(category, {"x": 300, "y": 300})
        
        # Offset for multiple components
        offset_x = (index % 4) * 200
        offset_y = (index // 4) * 150
        
        return {
            "x": base_pos["x"] + offset_x,
            "y": base_pos["y"] + offset_y
        }
    
    def _get_node_height(self, category: str) -> int:
        """Get appropriate height for node based on category."""
        category_heights = {
            "agents": 500,
            "prompts": 300,
            "tools": 350,
            "models": 400,
            "llms": 600,
            "outputs": 250,
            "inputs": 250
        }
        return category_heights.get(category, 350)
    
    def _filter_invalid_components(self, spec: Any, missing_components: List[str]) -> Any:
        """Filter out components that don't exist in Genesis Studio."""
        if hasattr(spec, "components"):
            spec.components = [
                comp for comp in spec.components
                if comp.get("type") not in missing_components
            ]
        elif isinstance(spec, dict) and "components" in spec:
            spec["components"] = [
                comp for comp in spec["components"]
                if comp.get("type") not in missing_components
            ]
            
        return spec
    
    def _get_output_types(self, node: Dict[str, Any], output_field: str) -> List[str]:
        """Get output types for a specific output field."""
        # Special case for component_as_tool
        if output_field == "component_as_tool":
            return ["Tool"]
            
        # Check node outputs
        outputs = node.get("data", {}).get("outputs", [])
        for output in outputs:
            if output.get("name") == output_field:
                types = output.get("types", [])
                if types:
                    return types
                    
        # Default types based on field name
        if "message" in output_field or "response" in output_field:
            return ["Message"]
        elif "prompt" in output_field:
            return ["Message", "str"]
        elif "tool" in output_field:
            return ["Tool"]
        else:
            return ["Message", "str"]
            
    def _get_input_types(self, node: Dict[str, Any], input_field: str) -> List[str]:
        """Get input types for a specific input field."""
        # Check template for input types
        template = node.get("data", {}).get("node", {}).get("template", {})
        if input_field in template:
            field_def = template[input_field]
            if isinstance(field_def, dict):
                input_types = field_def.get("input_types", [])
                if input_types:
                    return input_types
                    
        # Default types based on field name
        if input_field == "tools":
            return ["Tool"]
        elif input_field == "input_value":
            return ["Data", "DataFrame", "Message"]
        elif "message" in input_field:
            return ["Message"]
        else:
            return ["Message", "str"]
    
    def _is_component_used_as_tool(self, component: Dict[str, Any]) -> bool:
        """Check if a component is used as a tool based on its provides declarations."""
        provides = component.get("provides", [])
        for provide in provides:
            if provide.get("useAs") in ["tool", "tools"]:
                return True
        return False
    
    def _determine_handle_type(self, input_field: str, input_types: List[str]) -> str:
        """Determine the handle type based on Genesis Studio conventions.
        
        Genesis Studio uses specific values:
        - "other" for tools and multiple input types
        - "str" for Message inputs
        - Specific type name for single-type inputs
        """
        # Tools always use "other"
        if input_field == "tools":
            return "other"
            
        # Multiple input types use "other"
        if len(input_types) > 1:
            return "other"
            
        # Single Message type uses "str"
        if input_types and input_types[0] == "Message":
            return "str"
            
        # Single type uses the type name
        if input_types:
            return input_types[0]
            
        # Default to "str"
        return "str"
    
    def _validate_type_compatibility(self, output_types: List[str], input_types: List[str], 
                                   source_type: str, target_type: str) -> bool:
        """Validate if output types are compatible with input types.
        
        Returns True if compatible, False otherwise.
        """
        # Tool connections are always valid (Tools can connect to Tool inputs)
        if "Tool" in output_types and "Tool" in input_types:
            return True
            
        # Check for direct type matches
        if any(otype in input_types for otype in output_types):
            return True
            
        # Special case: Message -> Data incompatibility
        if "Message" in output_types and "Data" in input_types and "Message" not in input_types:
            # Specific components that cannot accept Message despite expecting Data
            incompatible_data_components = ["JSONOutput", "DataOutput", "ParseData"]
            if any(comp in target_type for comp in incompatible_data_components):
                return False
                
        # Check for compatible type conversions
        compatible_conversions = {
            "Message": ["str", "text", "Text"],
            "str": ["Message", "text", "Text"],
            "Data": ["dict", "object", "any"],
            "DataFrame": ["Data", "object", "any"]
        }
        
        for otype in output_types:
            if otype in compatible_conversions:
                if any(ctype in input_types for ctype in compatible_conversions[otype]):
                    return True
                    
        # If input accepts "any" or "object", it's compatible
        if "any" in input_types or "object" in input_types:
            return True
            
        # Default to incompatible
        return False
    
    def convert_sync(self, spec_path: str) -> Dict[str, Any]:
        """Synchronous wrapper for convert method."""
        import asyncio
        return asyncio.run(self.convert(spec_path))
    
    def apply_tweaks(self, flow: Dict[str, Any], tweaks: Dict[str, Any]) -> Dict[str, Any]:
        """Apply tweaks to the flow after conversion.
        
        Args:
            flow: The converted flow
            tweaks: Dictionary of tweaks to apply
            
        Returns:
            Flow with tweaks applied
        """
        return self.variable_resolver.apply_tweaks(flow, tweaks)
    
    def resolve_flow(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all variables in the flow.
        
        Args:
            flow: The flow to resolve
            
        Returns:
            Flow with all variables resolved
        """
        return self.variable_resolver.resolve_flow(flow)
    
    def validate_flow(self, flow: Dict[str, Any]) -> List[str]:
        """Validate the generated flow structure."""
        errors = []
        
        if "data" not in flow:
            errors.append("Missing 'data' field in flow")
            return errors
            
        data = flow["data"]
        
        # Check nodes
        if "nodes" not in data:
            errors.append("Missing 'nodes' in flow data")
        elif not data["nodes"]:
            errors.append("No nodes in flow")
            
        # Check edges
        if "edges" not in data:
            errors.append("Missing 'edges' in flow data")
            
        # Validate node structure
        for i, node in enumerate(data.get("nodes", [])):
            if "id" not in node:
                errors.append(f"Node {i} missing 'id'")
            if "type" not in node:
                errors.append(f"Node {i} missing 'type'")
            if "data" not in node:
                errors.append(f"Node {i} missing 'data'")
                
        # Validate edge structure
        for i, edge in enumerate(data.get("edges", [])):
            if "source" not in edge:
                errors.append(f"Edge {i} missing 'source'")
            if "target" not in edge:
                errors.append(f"Edge {i} missing 'target'")
            if "sourceHandle" not in edge:
                errors.append(f"Edge {i} missing 'sourceHandle'")
            if "targetHandle" not in edge:
                errors.append(f"Edge {i} missing 'targetHandle'")
                
        return errors