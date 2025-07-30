"""
Dynamic Component Mapper that fetches actual components from Genesis Studio.

This mapper dynamically loads component information from Genesis Studio API
and provides intelligent mapping for genesis: prefixed components.
"""

import json
import os
from typing import Dict, Optional, Any, Set
from datetime import datetime, timedelta
import httpx

from src.services.config import Config


class DynamicComponentMapper:
    """Maps Genesis component types to actual Genesis Studio components dynamically."""
    
    def __init__(self, config: Config):
        self.config = config
        self._components_cache: Dict[str, Any] = {}
        self._component_map: Dict[str, str] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self._cache_file = "genesis_components_cache.json"
        
    async def load_components(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Load components from Genesis Studio API or cache."""
        # Check if we should use cache
        if not force_refresh and self._is_cache_valid():
            return self._components_cache
            
        try:
            # Try to load from file cache first
            if not force_refresh and os.path.exists(self._cache_file):
                with open(self._cache_file, 'r') as f:
                    cache_data = json.load(f)
                    if 'timestamp' in cache_data:
                        cache_time = datetime.fromisoformat(cache_data['timestamp'])
                        if datetime.now() - cache_time < self._cache_duration:
                            self._components_cache = cache_data['components']
                            self._build_component_map()
                            print(f"✅ Loaded {len(self._get_all_components())} components from cache")
                            return self._components_cache
            
            # Fetch from API
            # Use the API key from config which already includes "Bearer "
            auth_header = self.config.api_key or ""
            if auth_header and not auth_header.startswith("Bearer "):
                auth_header = f"Bearer {auth_header}"
                
            headers = {
                "accept": "application/json",
                "Authorization": auth_header
            }
            
            # Ensure no double slashes
            base_url = self.config.genesis_studio_url.rstrip('/')
            url = f"{base_url}/api/v1/all?force_refresh=true"
            print(f"🔄 Fetching components from Genesis Studio: {url}")
            
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    # Handle gzipped response
                    components_data = response.json()
                    self._components_cache = components_data
                    self._cache_timestamp = datetime.now()
                    
                    # Save to file cache
                    with open(self._cache_file, 'w') as f:
                        json.dump({
                            'timestamp': self._cache_timestamp.isoformat(),
                            'components': components_data
                        }, f)
                    
                    self._build_component_map()
                    print(f"✅ Loaded {len(self._get_all_components())} components from Genesis Studio API")
                    
                else:
                    print(f"⚠️  Failed to fetch components: {response.status_code}")
                    self._load_fallback_components()
                    
        except Exception as e:
            print(f"⚠️  Error loading components: {e}")
            self._load_fallback_components()
            
        return self._components_cache
    
    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid."""
        if not self._cache_timestamp or not self._components_cache:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_duration
    
    def _get_all_components(self) -> Dict[str, Dict[str, Any]]:
        """Extract all components from the categorized structure."""
        all_components = {}
        
        for category, items in self._components_cache.items():
            if isinstance(items, dict):
                for comp_name, comp_data in items.items():
                    if isinstance(comp_data, dict) and 'display_name' in comp_data:
                        all_components[comp_name] = comp_data
                        
        return all_components
    
    def _build_component_map(self):
        """Build mapping from component names and types."""
        self._component_map.clear()
        
        # Get all components
        all_components = self._get_all_components()
        
        # Build mappings
        for comp_name, comp_data in all_components.items():
            # Map by component name
            self._component_map[comp_name.lower()] = comp_name
            
            # Map by display name
            if 'display_name' in comp_data:
                display_name = comp_data['display_name']
                self._component_map[display_name.lower().replace(' ', '_')] = comp_name
                self._component_map[display_name.lower().replace(' ', '')] = comp_name
                
            # Map common variations
            if comp_name == "AutonomizeAgent":
                self._component_map["autonomize_agent"] = comp_name
                self._component_map["agent"] = comp_name
            elif comp_name == "CustomComponent":
                self._component_map["custom"] = comp_name
                self._component_map["tool"] = comp_name
                
        print(f"📊 Built component map with {len(self._component_map)} mappings")
    
    def get_component_type(self, genesis_type: str) -> str:
        """
        Get the actual Genesis Studio component type for a genesis: prefixed type.
        
        Args:
            genesis_type: Component type (e.g., "genesis:autonomize_agent")
            
        Returns:
            Actual Genesis Studio component type
        """
        # Remove genesis: prefix if present
        if genesis_type.startswith("genesis:"):
            base_type = genesis_type[8:]  # Remove "genesis:"
        else:
            base_type = genesis_type
            
        # Normalize the type
        normalized = base_type.lower().replace('-', '_')
        
        # Direct mapping check
        if normalized in self._component_map:
            return self._component_map[normalized]
            
        # Intelligent mapping based on type patterns
        mapping_rules = {
            # Autonomize-specific components
            "autonomize_agent": "AutonomizeAgent",
            "agent": "Agent",
            
            # Models from autonomize_models category
            "rxnorm": "RxNorm",
            "icd10": "ICD10", 
            "cpt_code": "CPTCode",
            "clinical_note_classifier": "ClinicalNoteClassifier",
            "srf_extraction": "srf-extraction",
            "srf_identification": "srf-identification",
            "provider_llm": "AzureOpenAIModel",
            "clinical_llm": "ClinicalLLM",
            
            # I/O components
            "chat_input": "ChatInput",
            "chat_output": "ChatOutput",
            "json_output": "ParseData",
            "json_input": "JSONInput",
            
            # Memory
            "conversation_memory": "Memory",
            
            # Prompts
            "prompt_template": "PromptTemplate",
            
            # Most Genesis-specific tools should be CustomComponent
            "knowledge_hub_search": "CustomComponent",
            "pa_lookup": "CustomComponent",
            "eligibility_component": "CustomComponent",
            "encoder_pro": "CustomComponent",
            "qnext_auth_history": "CustomComponent",
            "api_component": "CustomComponent",
            "form_recognizer": "CustomComponent",
            "data_transformer": "CustomComponent",
            
            # Vector stores
            "vector_store": "QdrantVectorStore",
            
            # CrewAI
            "sequential_crew": "CrewAIAgent",
        }
        
        # Check mapping rules
        if normalized in mapping_rules:
            return mapping_rules[normalized]
            
        # Pattern-based fallbacks
        if "agent" in normalized:
            return "AutonomizeAgent"
        elif "tool" in normalized or "component" in normalized:
            return "CustomComponent"
        elif "llm" in normalized or "model" in normalized:
            # Check if it's a clinical model
            if any(term in normalized for term in ["clinical", "rxnorm", "icd", "cpt", "srf"]):
                return "CustomComponent"
            return "ProviderLLM"
        elif "memory" in normalized:
            return "Memory"
        elif "prompt" in normalized:
            return "Prompt"
        elif "input" in normalized:
            return "ChatInput"
        elif "output" in normalized:
            return "ChatOutput"
        else:
            # Default to CustomComponent for unknown Genesis components
            return "CustomComponent"
    
    def _load_fallback_components(self):
        """Load minimal fallback components when API is unavailable."""
        self._components_cache = {
            "agents": {
                "AutonomizeAgent": {"display_name": "Autonomize Agent"},
                "Agent": {"display_name": "Agent"}
            },
            "autonomize_models": {
                "RxNorm": {"display_name": "RxNorm Code"},
                "ICD10": {"display_name": "ICD-10 Code"},
                "CPTCode": {"display_name": "CPT Code"},
                "ProviderLLM": {"display_name": "Provider LLM"},
                "ClinicalLLM": {"display_name": "Clinical LLM"}
            },
            "custom_component": {
                "CustomComponent": {"display_name": "Custom Component"}
            },
            "inputs": {
                "ChatInput": {"display_name": "Chat Input"}
            },
            "outputs": {
                "ChatOutput": {"display_name": "Chat Output"},
                "ParseData": {"display_name": "Parse Data"}
            },
            "memories": {
                "MemoryComponent": {"display_name": "Memory Component"}
            },
            "prompts": {
                "Prompt": {"display_name": "Prompt"}
            }
        }
        self._build_component_map()
        print("ℹ️  Using fallback component mappings")
    
    def get_available_components(self) -> Set[str]:
        """Get set of all available component types."""
        return set(self._get_all_components().keys())
    
    def validate_component(self, component_type: str) -> bool:
        """Check if a component type is valid."""
        # Get the mapped type
        mapped_type = self.get_component_type(component_type)
        
        # Check if it exists in available components
        available = self.get_available_components()
        return mapped_type in available


# Global instance
_mapper_instance: Optional[DynamicComponentMapper] = None


async def get_dynamic_mapper(config: Config) -> DynamicComponentMapper:
    """Get or create the global dynamic mapper instance."""
    global _mapper_instance
    
    if _mapper_instance is None:
        _mapper_instance = DynamicComponentMapper(config)
        await _mapper_instance.load_components()
        
    return _mapper_instance


def get_langflow_component_type(genesis_type: str, config: Optional[Config] = None) -> str:
    """
    Synchronous wrapper for getting component type.
    Falls back to intelligent mapping if async mapper not available.
    """
    # If we have a cached mapper, use it
    if _mapper_instance:
        return _mapper_instance.get_component_type(genesis_type)
    
    # Otherwise use static intelligent mapping
    if genesis_type.startswith("genesis:"):
        base_type = genesis_type[8:]
    else:
        base_type = genesis_type
        
    # Intelligent static mapping
    static_map = {
        "autonomize_agent": "AutonomizeAgent",
        "chat_input": "ChatInput",
        "chat_output": "ChatOutput",
        "json_output": "ParseData",
        "prompt_template": "PromptTemplate",
        "conversation_memory": "Memory",
    }
    
    normalized = base_type.lower().replace('-', '_')
    if normalized in static_map:
        return static_map[normalized]
    
    # Pattern-based fallback
    if "agent" in normalized:
        return "AutonomizeAgent"
    elif any(term in normalized for term in ["tool", "component", "model", "llm"]):
        return "CustomComponent"
    else:
        return "CustomComponent"