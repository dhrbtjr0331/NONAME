from fastapi import APIRouter, HTTPException
import structlog

from app.config.settings import settings
from app.models.base_agent import (
    AgentInfo,
    AgentListResponse,
    AgentCapabilityRequest,
    AgentCapabilityResponse
)

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=AgentListResponse)
async def list_available_agents():
    """List all available AI agents"""
    try:
        agents = [
            AgentInfo(
                name="RFQ Assistant",
                description="Helps manufacturers create detailed Request for Quotations",
                capabilities=[
                    "Product specification guidance",
                    "Quantity and timeline planning",
                    "Quality requirements definition",
                    "Budget planning assistance",
                    "Industry best practices",
                    "RFQ completeness validation"
                ],
                status="active"
            )
            # Future agents can be added here:
            # - Supplier Analysis Agent
            # - Quote Comparison Agent
            # - Negotiation Assistant
            # - Contract Review Agent
        ]
        
        return AgentListResponse(
            agents=agents,
            total=len(agents)
        )
        
    except Exception as e:
        logger.error("Error listing agents", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")

@router.post("/capability-check", response_model=AgentCapabilityResponse)
async def check_agent_capability(request: AgentCapabilityRequest):
    """Check if an agent can handle a specific task"""
    try:
        task_lower = request.task_description.lower()
        
        if request.agent_name == "RFQ Assistant":
            # Check if the task is RFQ-related
            rfq_keywords = [
                "rfq", "request for quotation", "procurement", "sourcing",
                "specifications", "quote", "supplier", "vendor"
            ]
            
            can_handle = any(keyword in task_lower for keyword in rfq_keywords)
            confidence_score = 0.9 if can_handle else 0.1
            
            if can_handle:
                suggested_approach = "I can help you create a comprehensive RFQ by gathering product specifications, quantities, timelines, and quality requirements through an interactive conversation."
            else:
                suggested_approach = "This task doesn't seem to be related to RFQ creation. I specialize in helping with procurement and sourcing activities."
            
            return AgentCapabilityResponse(
                can_handle=can_handle,
                confidence_score=confidence_score,
                suggested_approach=suggested_approach
            )
        else:
            raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error checking agent capability", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to check capability: {str(e)}")

@router.get("/config")
async def get_agent_configuration():
    """Get current agent configuration"""
    return {
        "ai_provider": settings.AI_PROVIDER,
        "max_conversation_history": settings.MAX_CONVERSATION_HISTORY,
        "max_message_length": settings.MAX_MESSAGE_LENGTH,
        "conversation_timeout_minutes": settings.CONVERSATION_TIMEOUT_MINUTES,
        "default_temperature": settings.DEFAULT_MODEL_TEMPERATURE,
        "max_tokens": settings.MAX_TOKENS
    }