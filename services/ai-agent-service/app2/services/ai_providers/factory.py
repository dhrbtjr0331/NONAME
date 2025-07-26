"""
AI Provider Factory

Centralized factory for different LLM providers with automatic provider selection
based on configuration and API key availability.

Supported Providers:
- Mock: Simple mock responses for testing
- Anthropic: Claude API integration  
- OpenAI: GPT integration (future)
- AWS Bedrock: AWS managed models (future)
"""

from typing import Any, Dict
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)

def get_llm_provider():
    """
    Factory function to get the appropriate LLM provider based on settings
    
    Returns:
        Configured LLM provider instance
        
    Raises:
        ValueError: If provider is not supported or misconfigured
    """
    provider_name = settings.AI_PROVIDER.lower()
    
    try:
        if provider_name == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("Anthropic API key not found, falling back to mock provider")
                return _get_mock_provider()
            
            from .anthropic_provider import get_anthropic_llm
            logger.info("Using Anthropic Claude API provider")
            return get_anthropic_llm(
                model_name=settings.ANTHROPIC_MODEL,
                temperature=settings.DEFAULT_MODEL_TEMPERATURE
            )
            
        elif provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not found, falling back to mock provider")  
                return _get_mock_provider()
            # Future: OpenAI implementation
            raise NotImplementedError("OpenAI provider not yet implemented")
            
        elif provider_name == "bedrock":
            # Future: AWS Bedrock implementation
            raise NotImplementedError("Bedrock provider not yet implemented")
            
        elif provider_name == "mock":
            logger.info("Using mock LLM provider")
            return _get_mock_provider()
            
        else:
            raise ValueError(f"Unknown AI provider: {provider_name}")
            
    except Exception as e:
        logger.error(f"Failed to initialize {provider_name} provider: {e}")
        logger.info("Falling back to mock provider")
        return _get_mock_provider()

def _get_mock_provider():
    """Get mock provider for testing and development"""
    from .simple_mock import get_simple_mock_llm
    return get_simple_mock_llm()

def get_provider_info() -> Dict[str, Any]:
    """Get information about the current provider configuration"""
    try:
        provider = get_llm_provider()
        if hasattr(provider, 'get_model_info'):
            return provider.get_model_info()
        else:
            return {
                "provider": settings.AI_PROVIDER,
                "status": "active",
            }
    except Exception as e:
        return {
            "provider": settings.AI_PROVIDER,
            "status": "error", 
            "error": str(e)
        }

# Convenience exports
__all__ = [
    "get_llm_provider",
    "get_provider_info"
]