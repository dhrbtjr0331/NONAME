from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import structlog

from app.agents.rfq_assistant import RFQAssistant
from app.services.ai_providers.simple_mock import get_simple_mock_llm
from app.config.settings import settings

logger = structlog.get_logger()

router = APIRouter()

# Global agent instance (in production, you'd use dependency injection)
_rfq_agent = None

def get_rfq_agent() -> RFQAssistant:
    """Get or create RFQ agent instance"""
    global _rfq_agent
    if _rfq_agent is None:
        llm = get_simple_mock_llm()  # Start with simple mock, can switch to real LLM later
        _rfq_agent = RFQAssistant(llm=llm)
    return _rfq_agent

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    rfq_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    rfq_updates: Dict[str, Any]
    agent_name: str

@router.post("/rfq", response_model=ChatResponse)
async def chat_with_rfq_assistant(
    request: ChatRequest,
    agent: RFQAssistant = Depends(get_rfq_agent)
):
    """Chat with the RFQ assistant"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(
            "Processing RFQ chat request",
            session_id=session_id,
            user_id=request.user_id,
            message_length=len(request.message)
        )
        
        # Chat with the agent
        result = await agent.chat(
            message=request.message,
            session_id=session_id,
            rfq_data=request.rfq_data or {},
            user_id=request.user_id
        )
        
        logger.info(
            "RFQ chat response generated",
            session_id=session_id,
            response_length=len(result["response"])
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            rfq_updates=result["rfq_updates"],
            agent_name="RFQ Assistant"
        )
        
    except Exception as e:
        logger.error("Error processing RFQ chat", error=str(e), session_id=request.session_id)
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

class RFQSummaryRequest(BaseModel):
    session_id: str

class RFQSummaryResponse(BaseModel):
    summary: str
    rfq_data: Dict[str, Any]
    completeness_score: float

@router.post("/rfq/summary", response_model=RFQSummaryResponse)
async def get_rfq_summary(
    request: RFQSummaryRequest,
    agent: RFQAssistant = Depends(get_rfq_agent)
):
    """Get a summary of the current RFQ data for a session"""
    try:
        # In a real implementation, you'd retrieve the session data from storage
        # For now, we'll return a placeholder
        
        # This would typically retrieve the conversation state from the agent's memory
        rfq_data = {}  # Placeholder - would get from agent memory/database
        
        summary = agent.get_rfq_summary(rfq_data)
        
        # Calculate completeness score
        required_fields = ["product_name", "quantity", "timeline", "specifications"]
        completed_fields = sum(1 for field in required_fields if rfq_data.get(field))
        completeness_score = completed_fields / len(required_fields)
        
        return RFQSummaryResponse(
            summary=summary,
            rfq_data=rfq_data,
            completeness_score=completeness_score
        )
        
    except Exception as e:
        logger.error("Error getting RFQ summary", error=str(e), session_id=request.session_id)
        raise HTTPException(status_code=500, detail=f"Failed to get RFQ summary: {str(e)}")

@router.get("/health")
async def chat_health_check():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "agent_provider": settings.AI_PROVIDER
    }