"""
Component Loader Service - Dynamically loads available components from Genesis Studio.

This service fetches the actual components available in Genesis Studio/Langflow
and provides validation against them.
"""

import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import httpx

from src.services.config import Config
from src.services.genesis_studio_api import GenesisStudioAPI


class ComponentLoader:
    """Loads and caches available components from Genesis Studio."""
    
    def __init__(self, config: Config):
        self.config = config
        self.api = GenesisStudioAPI(config)
        self._component_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        
    async def load_components(self, force_refresh: bool = False, use_dynamic_mapper: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Load all available components from Genesis Studio.
        
        Args:
            force_refresh: Force a refresh of the cache
            
        Returns:
            Dictionary of component type to ComponentInfo
        """
        # Check if cache is valid
        if not force_refresh and self._cache_timestamp:
            if datetime.now() - self._cache_timestamp < self._cache_duration:
                return self._component_cache
                
        # Try to use dynamic mapper first
        if use_dynamic_mapper:
            try:
                from src.registry.dynamic_component_mapper import get_dynamic_mapper
                mapper = await get_dynamic_mapper(self.config)
                
                # Build component info from mapper's actual component data
                self._component_cache.clear()
                
                # Access the mapper's cached components data
                if hasattr(mapper, '_components_cache') and mapper._components_cache:
                    # Iterate through all categories
                    for category, components in mapper._components_cache.items():
                        if isinstance(components, dict):
                            for comp_name, comp_data in components.items():
                                if isinstance(comp_data, dict):
                                    # Store raw component data
                                    self._component_cache[comp_name] = comp_data
                
                self._cache_timestamp = datetime.now()
                print(f"✅ Loaded {len(self._component_cache)} components from dynamic mapper")
                return self._component_cache
                
            except Exception as e:
                print(f"⚠️  Could not use dynamic mapper: {e}")
                # Fall through to default loading
                
        try:
            # Fetch component types from Genesis Studio
            async with httpx.AsyncClient(follow_redirects=True) as client:
                # Try to get component types endpoint
                response = await client.get(
                    f"{self.config.genesis_studio_url}/api/v1/component-types/",
                    headers=self.api.headers,
                    timeout=30.0
                )
                
                if response.status_code == 404:
                    # Try alternative endpoint
                    response = await client.get(
                        f"{self.config.genesis_studio_url}/api/v1/types/",
                        headers=self.api.headers,
                        timeout=30.0
                    )
                
                response.raise_for_status()
                component_data = response.json()
                
                # Parse components
                self._component_cache.clear()
                
                # Handle different response formats
                if isinstance(component_data, dict):
                    # Response might be categorized
                    for category, components in component_data.items():
                        if isinstance(components, list):
                            for comp in components:
                                if "type" in comp:
                                    self._component_cache[comp["type"]] = comp
                        elif isinstance(components, dict):
                            for comp_type, comp_data in components.items():
                                self._component_cache[comp_type] = comp_data
                elif isinstance(component_data, list):
                    # Direct list of components
                    for comp in component_data:
                        if "type" in comp:
                            self._component_cache[comp["type"]] = comp
                        
                self._cache_timestamp = datetime.now()
                print(f"✅ Loaded {len(self._component_cache)} components from Genesis Studio")
                
        except Exception as e:
            print(f"⚠️  Failed to load components from API: {e}")
            # Fall back to known Langflow components
            self._load_default_components()
            
        return self._component_cache
    
    def _load_default_components(self):
        """Load default Langflow components as fallback."""
        default_components = {
            # Agents
            "Agent": {
                "type": "Agent",
                "display_name": "Agent",
                "category": "agents",
                "description": "Langflow Agent with LLM",
                "inputs": ["input_value", "tools"],
                "outputs": ["response"],
                "base_classes": ["Agent"],
                "icon": "Bot"
            },
            
            # LLMs
            "AzureOpenAIModel": {
                "type": "AzureOpenAIModel",
                "display_name": "Azure OpenAI",
                "category": "llms",
                "description": "Azure OpenAI language model",
                "inputs": ["input_value"],
                "outputs": ["text_output"],
                "base_classes": ["LanguageModel"],
                "icon": "Azure"
            },
            "OpenAIModel": {
                "type": "OpenAIModel",
                "display_name": "OpenAI",
                "category": "llms",
                "description": "OpenAI language model",
                "inputs": ["input_value"],
                "outputs": ["text_output"],
                "base_classes": ["LanguageModel"],
                "icon": "OpenAI"
            },
            
            # Tools
            "Tool": {
                "type": "Tool",
                "display_name": "Tool",
                "category": "tools",
                "description": "Generic tool component",
                "inputs": ["input_value"],
                "outputs": ["output"],
                "base_classes": ["Tool"],
                "icon": "Wrench"
            },
            "SearchAPI": {
                "type": "SearchAPI",
                "display_name": "Search API",
                "category": "tools",
                "description": "Web search tool",
                "inputs": ["query"],
                "outputs": ["results"],
                "base_classes": ["Tool"],
                "icon": "Globe"
            },
            
            # I/O
            "TextInput": {
                "type": "TextInput",
                "display_name": "Text Input",
                "category": "inputs",
                "description": "Text input component",
                "inputs": [],
                "outputs": ["text"],
                "base_classes": ["Input"],
                "icon": "Type"
            },
            "TextOutput": {
                "type": "TextOutput",
                "display_name": "Text Output",
                "category": "outputs",
                "description": "Text output component",
                "inputs": ["input_value"],
                "outputs": [],
                "base_classes": ["Output"],
                "icon": "FileText"
            },
            "ChatInput": {
                "type": "ChatInput",
                "display_name": "Chat Input",
                "category": "inputs",
                "description": "Chat input component",
                "inputs": [],
                "outputs": ["message"],
                "base_classes": ["Input"],
                "icon": "MessageSquare"
            },
            "ChatOutput": {
                "type": "ChatOutput",
                "display_name": "Chat Output",
                "category": "outputs",
                "description": "Chat output component",
                "inputs": ["input_value"],
                "outputs": [],
                "base_classes": ["Output"],
                "icon": "MessageSquare"
            },
            
            # Prompts
            "PromptTemplate": {
                "type": "PromptTemplate",
                "display_name": "Prompt Template",
                "category": "prompts",
                "description": "Prompt template",
                "inputs": ["template"],
                "outputs": ["prompt"],
                "base_classes": ["Prompt"],
                "icon": "FileText"
            },
            
            # Memory
            "ConversationBufferMemory": {
                "type": "ConversationBufferMemory",
                "display_name": "Conversation Buffer Memory",
                "category": "memory",
                "description": "Simple conversation memory",
                "inputs": [],
                "outputs": ["chat_history"],
                "base_classes": ["Memory"],
                "icon": "Database"
            },
            
            # Vector Stores
            "Qdrant": {
                "type": "Qdrant",
                "display_name": "Qdrant",
                "category": "vectorstores",
                "description": "Qdrant vector database",
                "inputs": ["documents"],
                "outputs": ["retriever"],
                "base_classes": ["VectorStore"],
                "icon": "Database"
            }
        }
        
        self._component_cache.clear()
        for comp_type, comp_data in default_components.items():
            self._component_cache[comp_type] = comp_data
            
        self._cache_timestamp = datetime.now()
        print(f"ℹ️  Loaded {len(self._component_cache)} default Langflow components")
    
    def validate_component(self, component_type: str) -> bool:
        """
        Validate if a component type exists.
        
        Args:
            component_type: Component type to validate
            
        Returns:
            True if component exists
        """
        # Remove genesis: prefix if present
        if component_type.startswith("genesis:"):
            # Map to actual component type
            try:
                from src.registry.dynamic_component_mapper import get_langflow_component_type
                component_type = get_langflow_component_type(component_type)
            except ImportError:
                from src.registry.component_type_mapper import get_langflow_component_type
                component_type = get_langflow_component_type(component_type)
            
        return component_type in self._component_cache
    
    def get_component_info(self, component_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a component.
        
        Args:
            component_type: Component type
            
        Returns:
            ComponentInfo or None if not found
        """
        # Remove genesis: prefix if present
        if component_type.startswith("genesis:"):
            try:
                from src.registry.dynamic_component_mapper import get_langflow_component_type
                component_type = get_langflow_component_type(component_type)
            except ImportError:
                from src.registry.component_type_mapper import get_langflow_component_type
                component_type = get_langflow_component_type(component_type)
            
        return self._component_cache.get(component_type)
    
    def get_available_components(self) -> List[str]:
        """Get list of available component types."""
        return list(self._component_cache.keys())
    
    def get_components_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all components in a category."""
        return [
            comp for comp in self._component_cache.values()
            if comp.get("category") == category
        ]


class ComponentValidator:
    """Validates agent specifications against available components."""
    
    def __init__(self, component_loader: ComponentLoader):
        self.loader = component_loader
        
    async def validate_spec(self, spec: Any) -> Dict[str, Any]:
        """
        Validate an agent specification against available components.
        
        Args:
            spec: Agent specification to validate
            
        Returns:
            Validation result with errors and warnings
        """
        # Ensure components are loaded
        await self.loader.load_components()
        
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_components": [],
            "available_components": []
        }
        
        # Extract all component types from spec
        component_types = self._extract_component_types(spec)
        
        # Validate each component
        for comp_type in component_types:
            if not self.loader.validate_component(comp_type):
                result["valid"] = False
                result["missing_components"].append(comp_type)
                
                # Try to find similar components
                similar = self._find_similar_components(comp_type)
                if similar:
                    result["warnings"].append(
                        f"Component '{comp_type}' not found. Similar: {', '.join(similar)}"
                    )
                else:
                    result["errors"].append(
                        f"Component '{comp_type}' not found in Genesis Studio"
                    )
            else:
                result["available_components"].append(comp_type)
                
        return result
    
    def _extract_component_types(self, spec: Any) -> Set[str]:
        """Extract all component types from a specification."""
        types = set()
        
        # Check components list
        if hasattr(spec, "components"):
            for comp in spec.components:
                if hasattr(comp, "type"):
                    types.add(comp.type)
                    
        # Check for v2 format
        if isinstance(spec, dict):
            # Check agent type
            if "agent" in spec and "type" in spec["agent"]:
                types.add(spec["agent"]["type"])
                
            # Check tools
            if "tools" in spec:
                for tool in spec["tools"]:
                    if "type" in tool:
                        types.add(tool["type"])
                        
            # Check outputs
            if "outputs" in spec:
                for output in spec["outputs"]:
                    if "type" in output:
                        types.add(output["type"])
                        
        return types
    
    def _find_similar_components(self, component_type: str) -> List[str]:
        """Find components with similar names."""
        similar = []
        
        # Extract base name
        base_name = component_type.lower()
        if base_name.startswith("genesis:"):
            base_name = base_name[8:]
            
        # Check for similar components
        for available_type in self.loader.get_available_components():
            if base_name in available_type.lower() or available_type.lower() in base_name:
                similar.append(available_type)
                
        return similar[:3]  # Return top 3 matches