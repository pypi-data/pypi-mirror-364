"""Component provides models for declarative connections."""

from typing import Optional, List
from pydantic import BaseModel, Field


class ComponentProvides(BaseModel):
    """Declares how a component provides data to other components."""
    
    useAs: str = Field(
        ..., 
        description="The field name in the target component (e.g., 'tools', 'input', 'system_prompt')"
    )
    in_: str = Field(
        ..., 
        alias="in",
        description="The ID of the target component"
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description of this connection"
    )
    
    class Config:
        """Allow 'in' as field name."""
        populate_by_name = True


class ComponentWithProvides(BaseModel):
    """Component definition with provides declarations."""
    
    id: str
    name: str
    kind: str
    type: str
    description: Optional[str] = None
    config: Optional[dict] = None
    provides: Optional[List[ComponentProvides]] = Field(
        None,
        description="List of connections this component provides to other components"
    )
    asTools: Optional[bool] = Field(
        False,
        description="Whether this component can be used as a tool"
    )