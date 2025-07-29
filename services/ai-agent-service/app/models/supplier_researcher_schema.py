from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ResearchPhase(Enum):
    PLANNING = "planning"
    DISCOVERY = "discovery" 
    EVALUATION = "evaluation"
    COMPLETE = "complete"

class SupplierResearchSchema(BaseModel):
    rfq_data: Dict[str, Any] = Field(None, description="RFQ data to guide supplier research")
    current_phase: ResearchPhase = Field(None, description="Current phase of the supplier research process")
    research_plan: Optional[Dict] = Field(None, description="Plan for the supplier research process, including tasks and objectives")
    supplier_candidates: List[Dict] = Field(None, description="List of potential suppliers identified during the research process")
    search_results: Dict[str, List] = Field(None, description="Search results from various sources, such as web scraping or API calls")
    evaluated_suppliers: List[Dict] = Field(None, description="List of suppliers evaluated based on criteria such as price, quality, and reliability")
    supplier_scores: Dict[str, float] = Field(None, description="Scores assigned to suppliers based on evaluation criteria")
    potential_suppliers: List[Dict] = Field(None, description = "List of potential suppliers identified during the research process. Ex. [{"company_name": "ABC Corp", "location": "Detroit", "score": 8.5}]")
    max_suppliers_to_find: int = Field(50, description="Maximum number of suppliers to find during the research process")
    target_suppliers: int = Field(30, description="Target number of suppliers to evaluate and shortlist")