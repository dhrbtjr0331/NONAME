from pydantic import BaseModel
from typing import List, Dict, Any

class AgentInfo(BaseModel):
    name: str
    description: str
    capabilities: List[str]
    status: str

class AgentListResponse(BaseModel):
    agents: List[AgentInfo]
    total: int

class AgentCapabilityRequest(BaseModel):
    agent_name: str
    task_description: str

class AgentCapabilityResponse(BaseModel):
    can_handle: bool
    confidence_score: float
    suggested_approach: str
