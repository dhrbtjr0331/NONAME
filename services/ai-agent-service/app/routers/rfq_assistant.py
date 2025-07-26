from fastapi import APIRouter, HTTPException, Depends
import uuid
import structlog

from langchain_anthropic import ChatAnthropic

from app.agents.rfq_assistant import RFQAssistant
from app.config.settings import settings
from app.models.rfq_assistant import (
    RFQChatResquest,
    RFQChatResponse,
    RFQSummaryRequest,
    RFQSummaryResponse
)

logger = structlog.get_logger()

router = APIRouter()

def get_rfq_agent() -> RFQAssistant:
    """Get or create RFQ agent instance"""
    
    # Fix the Pydantic model definition issue
    try:
        ChatAnthropic.model_rebuild()
    except Exception:
        pass  # In case it's already rebuilt or not needed
    
    llm = ChatAnthropic(
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        model=settings.ANTHROPIC_MODEL,
        temperature=0.7,
        max_tokens=settings.MAX_TOKENS,
        timeout=None,
        max_retries=2,   
    )
    rfq_agent = RFQAssistant(llm=llm)
    return rfq_agent
@router.post("/rfq", response_model=RFQChatResponse)
async def chat_with_rfq_assistant(
    request: RFQChatResquest,
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
            domain_data=request.rfq_data or {},
            user_id=request.user_id
        )
        
        logger.info(
            "RFQ chat response generated",
            session_id=session_id,
            response_length=len(result["response"])
        )
        
        return RFQChatResponse(
            response=result["response"],
            session_id=session_id,
            rfq_updates=result["domain_data"],
            agent_name="RFQ Assistant"
        )
        
    except Exception as e:
        logger.error("Error processing RFQ chat", error=str(e), session_id=request.session_id)
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

@router.post("/rfq/summary", response_model=RFQSummaryResponse)
async def get_rfq_summary(
    request: RFQSummaryRequest,
    agent: RFQAssistant = Depends(get_rfq_agent)
):
    """Get a summary of the current RFQ data for a session"""
    try:
        logger.info("Getting RFQ summary", session_id=request.session_id)
        
        # Get full RFQ summary from conversation history
        summary_data = await agent.get_rfq_summary(request.session_id)
        
        # Calculate completeness score
        required_fields = ["product_name", "quantity", "timeline", "budget_range"]
        rfq_data = summary_data.get("rfq_data", {})
        completed_fields = sum(1 for field in required_fields if rfq_data.get(field))
        completeness_score = completed_fields / len(required_fields) if required_fields else 0
        
        return RFQSummaryResponse(
            summary=summary_data.get("summary", "No RFQ data available"),
            rfq_data=rfq_data,
            completeness_score=completeness_score,
            conversation_length=summary_data.get("conversation_length", 0),
            next_steps=summary_data.get("next_steps", [])
        )
        
    except Exception as e:
        logger.error("Error getting RFQ summary", error=str(e), session_id=request.session_id)
        raise HTTPException(status_code=500, detail=f"Failed to get RFQ summary: {str(e)}")

@router.get("/health")
async def chat_health_check():
    """Health check for chat service"""
    provider_info = get_provider_info()
    return {
        "status": "healthy",
        "service": "chat",
        "ai_provider": settings.AI_PROVIDER,
        "provider_info": provider_info
    }