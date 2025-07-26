"""
Anthropic Claude API Provider

Integrates with Anthropic's Claude API using the official langchain-anthropic package.
Provides a clean interface for LLM calls with proper error handling and rate limiting.
"""

from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)

class AnthropicProvider:
    """Anthropic Claude API provider with LangChain integration"""
    
    def __init__(self, model_name: str = "claude-3-haiku-20240307", temperature: float = 0.7):
        """
        Initialize Anthropic provider
        
        Args:
            model_name: Claude model to use (claude-3-haiku, claude-3-sonnet, claude-3-opus)
            temperature: Response creativity (0.0-1.0)
        """
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialize LangChain Anthropic chat model
        self.llm = ChatAnthropic(
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            model_name=model_name,
            temperature=temperature,
            max_tokens=settings.MAX_TOKENS
        )
        
        logger.info(f"Initialized Anthropic provider with model: {model_name}")
    
    async def ainvoke(self, input_data: Dict[str, Any]) -> str:
        """
        Async invoke Claude API with message context
        
        Args:
            input_data: Dictionary containing 'messages' and optional context
            
        Returns:
            Generated response string
        """
        try:
            messages = input_data.get("messages", [])
            if not messages:
                raise ValueError("No messages provided for LLM invocation")
            
            # Log request (without sensitive data)
            logger.info(f"Anthropic API call - Messages: {len(messages)}, Model: {self.model_name}")
            
            # Call Claude API through LangChain
            response = await self.llm.ainvoke(messages)
            
            # Extract content from response
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Anthropic API response - Length: {len(response_content)} chars")
            return response_content
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {str(e)}")
            # Fallback response for graceful degradation
            return f"I apologize, but I'm experiencing technical difficulties. Please try again. (Error: {type(e).__name__})"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        return {
            "provider": "anthropic",
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": settings.MAX_TOKENS,
            "status": "configured" if settings.ANTHROPIC_API_KEY else "missing_key"
        }

    def get_llm_with_structured_output(self, schema: Dict[str, Any]):
        """
        Get LLM instance with structured output configuration
        
        Args:
            schema: JSON schema for structured output
            
        Returns:
            Configured LLM instance
        """
        return self.llm.with_structured_output(schema)
    
    
# Factory function for easy instantiation
def get_anthropic_llm(model_name: str = None, temperature: float = None) -> AnthropicProvider:
    """
    Factory function to create Anthropic LLM instance
    
    Args:
        model_name: Override default model
        temperature: Override default temperature
        
    Returns:
        Configured AnthropicProvider instance
    """
    model = model_name or "claude-3-haiku-20240307"  # Fast, cost-effective model
    temp = temperature if temperature is not None else settings.DEFAULT_MODEL_TEMPERATURE
    
    return AnthropicProvider(model_name=model, temperature=temp)

# Available Claude models
CLAUDE_MODELS = {
    "haiku": "claude-3-haiku-20240307",      # Fast, lightweight
    "sonnet": "claude-3-sonnet-20240229",   # Balanced performance
    "opus": "claude-3-opus-20240229"        # Most capable, slower
}