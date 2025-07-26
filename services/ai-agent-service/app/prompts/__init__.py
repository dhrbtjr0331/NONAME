"""
Prompts Package

Centralized collection of all AI agent prompts organized by agent type.
This structure provides:

- Clean separation of prompts from business logic
- Easy maintenance and versioning
- Reusability across similar agents
- A/B testing capability
- Version control of prompt changes

Usage:
    from app.prompts.rfq_assistant import SYSTEM_PROMPT, get_data_extraction_prompt
    from app.prompts.supplier_agent import SYSTEM_PROMPT as SUPPLIER_SYSTEM_PROMPT
"""

# Version tracking for prompt package
__version__ = "1.0.0"
__last_updated__ = "2024-07-19"

# Import commonly used prompts for easy access
from .base import (
    format_json_instruction,
    format_conversation_context,
    format_data_for_prompt,
    PROFESSIONAL_TONE,
    JSON_RESPONSE_INSTRUCTION,
    CONVERSATION_GUIDELINES,
)

from .rfq_assistant import (
    SYSTEM_PROMPT as RFQ_SYSTEM_PROMPT,
    get_data_extraction_prompt as get_rfq_extraction_prompt,
    get_context_analysis_prompt as get_rfq_context_prompt,
    get_next_question_prompt as get_rfq_question_prompt,
    get_next_steps_prompt as get_rfq_steps_prompt,
)

# Future imports when we add more agents
# from .supplier_agent import SYSTEM_PROMPT as SUPPLIER_SYSTEM_PROMPT
# from .quote_analyzer import SYSTEM_PROMPT as QUOTE_SYSTEM_PROMPT

__all__ = [
    # Base utilities
    "format_json_instruction",
    "format_conversation_context", 
    "format_data_for_prompt",
    "PROFESSIONAL_TONE",
    "JSON_RESPONSE_INSTRUCTION",
    "CONVERSATION_GUIDELINES",
    
    # RFQ Assistant
    "RFQ_SYSTEM_PROMPT",
    "get_rfq_extraction_prompt", 
    "get_rfq_context_prompt",
    "get_rfq_question_prompt",
    "get_rfq_steps_prompt",
]