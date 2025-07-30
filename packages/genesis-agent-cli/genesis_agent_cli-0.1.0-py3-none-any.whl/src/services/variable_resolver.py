"""
Variable Resolver - Runtime variable substitution and tweaks for Genesis flows.

This module provides:
1. Variable substitution in flow configurations using {variable_name} syntax
2. Environment variable fallback with ${ENV_VAR} syntax
3. Tweaks system for runtime flow modifications
4. Type-safe variable validation
"""

import os
import re
from typing import Dict, Any, Optional, Union, List, Set
from datetime import datetime
import json
from pathlib import Path


class VariableResolver:
    """Resolves variables and applies tweaks to flow configurations."""
    
    # Pattern for runtime variables: {variable_name}
    RUNTIME_VAR_PATTERN = re.compile(r'\{([^}]+)\}')
    
    # Pattern for environment variables: ${ENV_VAR}
    ENV_VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    # Pattern for nested access: {config.api_key}
    NESTED_VAR_PATTERN = re.compile(r'\{([^}]+\.+[^}]+)\}')
    
    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        """Initialize the variable resolver.
        
        Args:
            variables: Dictionary of runtime variables to use for substitution
        """
        self.variables = variables or {}
        self._resolved_cache = {}
        self.undefined_vars: Set[str] = set()
        
    def set_variable(self, key: str, value: Any) -> None:
        """Set a runtime variable.
        
        Args:
            key: Variable name
            value: Variable value
        """
        self.variables[key] = value
        # Clear cache when variables change
        self._resolved_cache.clear()
        
    def set_variables(self, variables: Dict[str, Any]) -> None:
        """Set multiple runtime variables.
        
        Args:
            variables: Dictionary of variables to set
        """
        self.variables.update(variables)
        self._resolved_cache.clear()
        
    def resolve(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Resolve variables in a value recursively.
        
        Args:
            value: Value to resolve (can be str, dict, list, or any type)
            context: Additional context variables for this resolution
            
        Returns:
            Resolved value with all variables substituted
        """
        # Merge context with instance variables
        effective_vars = {**self.variables}
        if context:
            effective_vars.update(context)
            
        return self._resolve_value(value, effective_vars)
    
    def _resolve_value(self, value: Any, variables: Dict[str, Any]) -> Any:
        """Recursively resolve variables in a value."""
        if isinstance(value, str):
            return self._resolve_string(value, variables)
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, variables) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_value(v, variables) for v in value]
        else:
            # Non-string, non-collection values are returned as-is
            return value
            
    def _resolve_string(self, value: str, variables: Dict[str, Any]) -> Union[str, Any]:
        """Resolve variables in a string value.
        
        Supports:
        - Runtime variables: {variable_name}
        - Environment variables: ${ENV_VAR}
        - Nested access: {config.api_key}
        - Type preservation: If the entire string is a variable, preserve its type
        """
        # Check if the entire string is a single variable reference
        if value.strip().startswith('{') and value.strip().endswith('}'):
            var_match = self.RUNTIME_VAR_PATTERN.match(value.strip())
            if var_match and var_match.group(0) == value.strip():
                var_name = var_match.group(1)
                resolved = self._get_variable_value(var_name, variables)
                if resolved is not None:
                    # Return the actual value, preserving type
                    return resolved
                else:
                    self.undefined_vars.add(var_name)
                    return value  # Keep original if not found
        
        # Check for environment variable (entire string)
        if value.strip().startswith('${') and value.strip().endswith('}'):
            env_match = self.ENV_VAR_PATTERN.match(value.strip())
            if env_match and env_match.group(0) == value.strip():
                env_var = env_match.group(1)
                env_value = os.getenv(env_var)
                if env_value is not None:
                    # Try to parse as JSON to preserve type
                    try:
                        return json.loads(env_value)
                    except json.JSONDecodeError:
                        return env_value
                else:
                    return value  # Keep original if not found
        
        # Otherwise, do string substitution
        result = value
        
        # Replace runtime variables
        for match in self.RUNTIME_VAR_PATTERN.finditer(value):
            var_name = match.group(1)
            var_value = self._get_variable_value(var_name, variables)
            if var_value is not None:
                # Convert to string for substitution
                result = result.replace(match.group(0), str(var_value))
            else:
                self.undefined_vars.add(var_name)
                
        # Replace environment variables
        for match in self.ENV_VAR_PATTERN.finditer(result):
            env_var = match.group(1)
            env_value = os.getenv(env_var, match.group(0))
            result = result.replace(match.group(0), env_value)
            
        return result
    
    def _get_variable_value(self, var_name: str, variables: Dict[str, Any]) -> Any:
        """Get variable value, supporting nested access."""
        # Check for nested access (e.g., config.api_key)
        if '.' in var_name:
            parts = var_name.split('.')
            value = variables
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        else:
            return variables.get(var_name)
            
    def get_undefined_variables(self) -> List[str]:
        """Get list of variables that were referenced but not defined."""
        return list(self.undefined_vars)
        
    def clear_undefined_variables(self) -> None:
        """Clear the list of undefined variables."""
        self.undefined_vars.clear()
        
    def apply_tweaks(self, flow: Dict[str, Any], tweaks: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply tweaks to a flow configuration.
        
        Tweaks are runtime modifications to specific components in the flow.
        
        Args:
            flow: The flow configuration
            tweaks: Dictionary of tweaks to apply. If None, uses self.tweaks
            
        Returns:
            Modified flow with tweaks applied
        """
        if tweaks is None:
            tweaks = getattr(self, 'tweaks', {})
        # Deep copy to avoid modifying original
        import copy
        flow_copy = copy.deepcopy(flow)
        
        # Handle tweaks in format "component_id.field" = value
        if tweaks:
            parsed_tweaks = {}
            for key, value in tweaks.items():
                if '.' in key:
                    component_id, field = key.split('.', 1)
                    if component_id not in parsed_tweaks:
                        parsed_tweaks[component_id] = {}
                    parsed_tweaks[component_id][field] = value
                else:
                    parsed_tweaks[key] = value
            
            # Apply tweaks to nodes
            if "data" in flow_copy and "nodes" in flow_copy["data"]:
                for node in flow_copy["data"]["nodes"]:
                    node_id = node.get("id")
                    if node_id in parsed_tweaks:
                        self._apply_node_tweaks(node, parsed_tweaks[node_id])
                    
        return flow_copy
    
    def _apply_node_tweaks(self, node: Dict[str, Any], tweaks: Dict[str, Any]) -> None:
        """Apply tweaks to a specific node."""
        # Apply tweaks to node template
        if "data" in node and "node" in node["data"] and "template" in node["data"]["node"]:
            template = node["data"]["node"]["template"]
            
            for field_name, field_value in tweaks.items():
                if field_name in template:
                    # Convert string values to appropriate types
                    if isinstance(field_value, str):
                        try:
                            # Try to convert to number
                            if '.' in field_value:
                                field_value = float(field_value)
                            else:
                                field_value = int(field_value)
                        except ValueError:
                            # Keep as string
                            pass
                    # Resolve variables in the tweak value
                    resolved_value = self.resolve(field_value)
                    template[field_name]["value"] = resolved_value
                    
    def resolve_flow(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all variables in a flow configuration.
        
        Args:
            flow: The flow configuration
            
        Returns:
            Flow with all variables resolved
        """
        return self.resolve(flow)
        
    def create_tweaks_from_cli(self, tweak_args: List[str]) -> Dict[str, Any]:
        """Create tweaks dictionary from CLI arguments.
        
        Args:
            tweak_args: List of tweak arguments in format "component_id.field=value"
            
        Returns:
            Dictionary of tweaks
        """
        tweaks = {}
        
        for tweak in tweak_args:
            if '=' not in tweak:
                raise ValueError(f"Invalid tweak format: {tweak}. Expected format: component_id.field=value")
                
            key_path, value = tweak.split('=', 1)
            
            if '.' not in key_path:
                raise ValueError(f"Invalid tweak key: {key_path}. Expected format: component_id.field")
                
            parts = key_path.split('.')
            component_id = parts[0]
            field_name = '.'.join(parts[1:])
            
            # Try to parse value as JSON
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # If not valid JSON, treat as string
                parsed_value = value
                
            # Build nested structure
            if component_id not in tweaks:
                tweaks[component_id] = {}
            tweaks[component_id][field_name] = parsed_value
            
        return tweaks
        
    def load_variables_from_file(self, file_path: Union[str, Path]) -> None:
        """Load variables from a JSON or YAML file.
        
        Args:
            file_path: Path to variables file
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Variables file not found: {file_path}")
            
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                import yaml
                variables = yaml.safe_load(f)
            elif path.suffix == '.json':
                variables = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}. Use .json or .yaml")
                
        if not isinstance(variables, dict):
            raise ValueError("Variables file must contain a dictionary")
            
        self.set_variables(variables)
        
    def get_required_variables(self, value: Any) -> Set[str]:
        """Extract all variable references from a value.
        
        Args:
            value: Value to analyze
            
        Returns:
            Set of variable names referenced
        """
        variables = set()
        self._extract_variables(value, variables)
        return variables
        
    def _extract_variables(self, value: Any, variables: Set[str]) -> None:
        """Recursively extract variable references."""
        if isinstance(value, str):
            # Extract runtime variables
            for match in self.RUNTIME_VAR_PATTERN.finditer(value):
                variables.add(match.group(1))
            # Extract environment variables
            for match in self.ENV_VAR_PATTERN.finditer(value):
                variables.add(f"${{{match.group(1)}}}")
        elif isinstance(value, dict):
            for v in value.values():
                self._extract_variables(v, variables)
        elif isinstance(value, list):
            for v in value:
                self._extract_variables(v, variables)
                
    def validate_variables(self, required_vars: Set[str]) -> Dict[str, List[str]]:
        """Validate that all required variables are available.
        
        Args:
            required_vars: Set of required variable names
            
        Returns:
            Dictionary with 'missing' and 'available' lists
        """
        missing = []
        available = []
        
        for var in required_vars:
            if var.startswith('${') and var.endswith('}'):
                # Environment variable
                env_var = var[2:-1]
                if os.getenv(env_var) is None:
                    missing.append(var)
                else:
                    available.append(var)
            else:
                # Runtime variable
                if self._get_variable_value(var, self.variables) is None:
                    missing.append(var)
                else:
                    available.append(var)
                    
        return {
            'missing': missing,
            'available': available
        }
    
    def resolve_dict(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve variables in a dictionary."""
        return self._resolve_value(obj, self.variables)
        
    def resolve_list(self, lst: List[Any]) -> List[Any]:
        """Recursively resolve variables in a list."""
        return self._resolve_value(lst, self.variables)
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load variables from a JSON or YAML file.
        
        Args:
            file_path: Path to variables file
            
        Returns:
            Dictionary of variables
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Variables file not found: {file_path}")
            
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                import yaml
                return yaml.safe_load(f)
            elif path.suffix == '.json':
                return json.load(f)
            else:
                # Try to parse as JSON first, then YAML
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    import yaml
                    return yaml.safe_load(content)
    
    @staticmethod
    def parse_var_string(var_str: str) -> Dict[str, Any]:
        """Parse a variable string from CLI (key=value format).
        
        Args:
            var_str: Variable string in format "key=value" or "a.b.c=value"
            
        Returns:
            Dictionary with parsed variable
        """
        if '=' not in var_str:
            raise ValueError(f"Invalid variable format: {var_str}. Expected key=value")
            
        key, value = var_str.split('=', 1)
        
        # Parse the value
        if value.lower() == 'true':
            parsed_value = True
        elif value.lower() == 'false':
            parsed_value = False
        else:
            try:
                # Try int
                parsed_value = int(value)
            except ValueError:
                try:
                    # Try float
                    parsed_value = float(value)
                except ValueError:
                    # Keep as string
                    parsed_value = value
        
        # Handle nested keys (a.b.c=value)
        if '.' in key:
            parts = key.split('.')
            result = {}
            current = result
            for i, part in enumerate(parts[:-1]):
                current[part] = {}
                current = current[part]
            current[parts[-1]] = parsed_value
            return result
        else:
            return {key: parsed_value}