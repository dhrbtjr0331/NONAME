from fastapi import APIRouter, HTTPException, Depends
import uuid
import structlog

from langchain_anthropic import ChatAnthropic

from app.agents.supplier_research_agent import SupplierResearchAgent
from app.config.settings import settings
from app.models.supplier_research import (
    SupplierResearchRequest,
    SupplierResearchResponse,
    SupplierChatRequest,
    SupplierChatResponse
)

logger = structlog.get_logger()

router = APIRouter()

def get_supplier_research_agent() -> SupplierResearchAgent:
    """Get or create Supplier Research agent instance"""
    
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
    supplier_agent = SupplierResearchAgent(llm=llm)
    return supplier_agent


@router.post("/supplier-research", response_model=SupplierResearchResponse)
async def find_suppliers_for_rfq(
    request: SupplierResearchRequest,
    agent: SupplierResearchAgent = Depends(get_supplier_research_agent)
):
    """Find suppliers for an RFQ using the Supplier Research Agent"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(
            "Processing supplier research request",
            session_id=session_id,
            user_id=request.user_id,
            rfq_keys=list(request.rfq_data.keys()) if request.rfq_data else []
        )
        
        # Find suppliers using the agent
        result = await agent.find_suppliers_for_rfq(
            rfq_data=request.rfq_data,
            session_id=session_id,
            user_id=request.user_id
        )
        
        logger.info(
            "Supplier research completed",
            session_id=session_id,
            suppliers_found=len(result["suppliers"])
        )
        
        return SupplierResearchResponse(
            suppliers=result["suppliers"],
            search_summary=result["search_summary"],
            session_id=session_id,
            agent_name="Supplier Researcher"
        )
        
    except Exception as e:
        logger.error(
            "Error processing supplier research", 
            error=str(e), 
            session_id=request.session_id
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process supplier research: {str(e)}"
        )


@router.post("/supplier-research/chat", response_model=SupplierChatResponse)
async def chat_with_supplier_agent(
    request: SupplierChatRequest,
    agent: SupplierResearchAgent = Depends(get_supplier_research_agent)
):
    """Chat with the Supplier Research agent for follow-up questions"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(
            "Processing supplier research chat request",
            session_id=session_id,
            user_id=request.user_id,
            message_length=len(request.message)
        )
        
        # Chat with the agent using the base chat method
        result = await agent.chat(
            message=request.message,
            session_id=session_id,
            domain_data=request.domain_data or {},
            user_id=request.user_id
        )
        
        logger.info(
            "Supplier research chat response generated",
            session_id=session_id,
            response_length=len(result["response"])
        )
        
        return SupplierChatResponse(
            response=result["response"],
            session_id=session_id,
            updated_data=result["domain_data"],
            agent_name="Supplier Researcher"
        )
        
    except Exception as e:
        logger.error(
            "Error processing supplier research chat", 
            error=str(e), 
            session_id=request.session_id
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat: {str(e)}"
        )


@router.get("/supplier-research/status/{session_id}")
async def get_research_status(
    session_id: str,
    agent: SupplierResearchAgent = Depends(get_supplier_research_agent)
):
    """Get the current status of a supplier research session"""
    try:
        logger.info("Getting research status", session_id=session_id)
        
        # Retrieve the session state from the agent
        session_state = agent.get_session_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=404,
                detail=f"Session with ID {session_id} not found"
            )
        
        return {
            "session_id": session_id,
            "status": session_state.get("status", "unknown"),
            "progress": session_state.get("progress", 0),
            "message": session_state.get("message", "No additional information available")
        }
        
    except Exception as e:
        logger.error("Error getting research status", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get status: {str(e)}"
        )