"""Genesis Studio API client for managing flows/agents."""

from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from pydantic import BaseModel, Field

from src.services.config import Config


class FlowData(BaseModel):
    """Langflow flow data structure."""

    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    viewport: Dict[str, Any] = Field(default_factory=dict)


class Flow(BaseModel):
    """Flow/Agent model from Genesis Studio."""

    id: UUID
    name: str
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    endpoint_name: Optional[str] = None
    is_component: bool = False
    updated_at: Optional[str] = None
    folder_id: Optional[UUID] = None
    user_id: Optional[UUID] = None


class FlowCreate(BaseModel):
    """Flow creation request model."""

    name: str
    description: Optional[str] = None
    data: Dict[str, Any]
    endpoint_name: Optional[str] = None
    is_component: bool = False


class GenesisStudioAPI:
    """Client for Genesis Studio API."""

    def __init__(self, config: Config):
        """Initialize API client.

        Args:
            config: Configuration object
        """
        self.config = config
        self.base_url = config.genesis_studio_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
        }
        # Support both api_key and bearer_token
        if config.api_key:
            # If it starts with "Bearer ", use as-is, otherwise add Bearer prefix
            if config.api_key.startswith("Bearer "):
                self.headers["Authorization"] = config.api_key
            else:
                self.headers["Authorization"] = f"Bearer {config.api_key}"

    async def list_flows(self) -> List[Flow]:
        """List all flows/agents.

        Returns:
            List of flows
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/flows/",
                headers=self.headers,
            )
            response.raise_for_status()

            flows_data = response.json()
            return [Flow(**flow) for flow in flows_data]

    async def get_flow(self, flow_id: str) -> Flow:
        """Get a specific flow/agent.

        Args:
            flow_id: Flow ID

        Returns:
            Flow object
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/flows/{flow_id}/",
                headers=self.headers,
            )
            response.raise_for_status()

            return Flow(**response.json())

    async def create_flow(self, flow: FlowCreate) -> Flow:
        """Create a new flow/agent.

        Args:
            flow: Flow creation data

        Returns:
            Created flow
        """
        request_data = flow.model_dump(exclude_none=True)

        # Debug: Check if edges are in the request
        if "data" in request_data and "edges" in request_data["data"]:
            edges = request_data["data"]["edges"]
            print(f"\n=== API REQUEST DEBUG ===")
            print(f"Sending {len(edges)} edges in API request:")
            for i, edge in enumerate(edges):
                print(
                    f"  Edge {i+1}: {edge.get('source', '?')} -> {edge.get('target', '?')}"
                )
        else:
            print(f"\n❌ No edges found in API request data!")

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/flows/",
                headers=self.headers,
                json=request_data,
            )
            response.raise_for_status()

            # Debug: Check if edges are in the response
            response_data = response.json()
            if "data" in response_data and "edges" in response_data["data"]:
                response_edges = response_data["data"]["edges"]
                print(f"Received {len(response_edges)} edges in API response")
            else:
                print(f"❌ No edges found in API response!")

            return Flow(**response_data)

    async def update_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Flow:
        """Update an existing flow/agent.

        Args:
            flow_id: Flow ID
            flow_data: Updated flow data

        Returns:
            Updated flow
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.patch(
                f"{self.base_url}/api/v1/flows/{flow_id}/",
                headers=self.headers,
                json=flow_data,
            )
            response.raise_for_status()

            return Flow(**response.json())

    async def delete_flow(self, flow_id: str) -> None:
        """Delete a flow/agent.

        Args:
            flow_id: Flow ID
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/api/v1/flows/{flow_id}/",
                headers=self.headers,
            )
            response.raise_for_status()

    async def check_health(self) -> bool:
        """Check if Genesis Studio is accessible.

        Returns:
            True if healthy
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/flows/",
                    headers=self.headers,
                )
                return response.status_code == 200
        except Exception:
            return False
