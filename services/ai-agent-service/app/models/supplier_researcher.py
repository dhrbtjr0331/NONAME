# app/models/supplier_researcher.py

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SupplierInfo(BaseModel):
    """Individual supplier information"""
    company_name: str = Field(..., description="Company name")
    score: float = Field(..., ge=0, le=10, description="Supplier score (0-100)")
    reasoning: Optional[str] = Field(None, description="Reasoning for the score")
    location: Optional[str] = Field(None, description="Company location")
    website: Optional[str] = Field(None, description="Company website")
    source: Optional[str] = Field(None, description="Discovery source")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Company certifications")
    contact_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contact information")


class SupplierResearchRequest(BaseModel):
    """Request model for supplier research"""
    rfq_data: Dict[str, Any] = Field(..., description="RFQ data to research suppliers for")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")
    max_suppliers: Optional[int] = Field(20, ge=1, le=100, description="Maximum suppliers to find")
    target_suppliers: Optional[int] = Field(10, ge=1, le=50, description="Target number of suppliers")
    research_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Research preferences (geographic, industry, etc.)"
    )


class SupplierResearchResponse(BaseModel):
    """Response model for supplier research"""
    suppliers: List[SupplierInfo] = Field(..., description="List of found suppliers")
    search_summary: str = Field(..., description="Summary of the search process")
    session_id: str = Field(..., description="Session ID for tracking")
    agent_name: str = Field(default="Supplier Researcher", description="Agent name")
    total_candidates_found: Optional[int] = Field(None, description="Total candidates discovered")
    research_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Metadata about the research process"
    )


class SupplierChatRequest(BaseModel):
    """Request model for chatting with supplier research agent"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    domain_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Current supplier research data"
    )


class SupplierChatResponse(BaseModel):
    """Response model for supplier research chat"""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    updated_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Updated supplier research data"
    )
    agent_name: str = Field(default="Supplier Researcher", description="Agent name")
    suggestions: Optional[List[str]] = Field(
        default_factory=list, 
        description="Suggested follow-up actions"
    )


class ResearchStatusResponse(BaseModel):
    """Response model for research status"""
    session_id: str = Field(..., description="Session ID")
    current_phase: str = Field(..., description="Current research phase")
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    suppliers_found: int = Field(default=0, description="Number of suppliers found so far")
    status: str = Field(..., description="Current status (active, completed, error)")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    next_steps: Optional[List[str]] = Field(
        default_factory=list, 
        description="Suggested next steps"
    )