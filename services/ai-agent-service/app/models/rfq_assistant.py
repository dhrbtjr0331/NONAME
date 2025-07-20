from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class RFQChatResquest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    rfq_data: Optional[Dict[str, Any]] = None

class RFQChatResponse(BaseModel):
    response: str
    session_id: str
    rfq_updates: Dict[str, Any]
    agent_name: str

class RFQSummaryRequest(BaseModel):
    session_id: str

class RFQSummaryResponse(BaseModel):
    summary: str
    rfq_data: Dict[str, Any]
    completeness_score: float
    conversation_length: int = 0
    next_steps: List[str] = []