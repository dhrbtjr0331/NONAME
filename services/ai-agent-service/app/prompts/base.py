"""
Base Prompts Collection

Common prompts and prompt utilities that can be shared across different agent types.
This includes:
- Generic system prompt templates
- Common data extraction patterns
- Shared utility functions
- Base conversation patterns
"""

# =============================================================================
# COMMON PROMPT UTILITIES
# =============================================================================

def format_json_instruction(fields_description: str) -> str:
    """Generate consistent JSON format instructions"""
    return f"""
{fields_description}

Return ONLY a valid JSON object with the extracted information.
If no relevant information is found, return an empty object {{}}.

JSON Response:"""

def format_conversation_context(messages: list, max_messages: int = 6) -> str:
    """Format recent conversation messages for prompt context"""
    if not messages:
        return "No previous conversation context."
    
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
    formatted_messages = []
    
    for msg in recent_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        # Truncate long messages
        content = content[:200] + "..." if len(content) > 200 else content
        formatted_messages.append(f"{role.title()}: {content}")
    
    return "\n".join(formatted_messages)

def format_data_for_prompt(data: dict, title: str = "Current Data") -> str:
    """Format dictionary data for inclusion in prompts"""
    if not data:
        return f"{title}: No data available."
    
    formatted_items = []
    for key, value in data.items():
        if value is not None and value != "":
            # Convert snake_case to Title Case
            display_key = key.replace('_', ' ').title()
            formatted_items.append(f"- {display_key}: {value}")
    
    if not formatted_items:
        return f"{title}: No data available."
    
    return f"{title}:\n" + "\n".join(formatted_items)

# =============================================================================
# COMMON SYSTEM PROMPT COMPONENTS
# =============================================================================

PROFESSIONAL_TONE = """
Maintain a professional, helpful, and consultative tone throughout the conversation.
Be clear, concise, and focused on gathering actionable information.
"""

JSON_RESPONSE_INSTRUCTION = """
Respond ONLY with valid JSON. Do not include explanations, markdown formatting, or additional text outside the JSON structure.
"""

CONVERSATION_GUIDELINES = """
Guidelines for effective conversation:
1. Ask ONE focused question at a time
2. Build on previous answers intelligently  
3. Don't repeat questions already answered
4. Offer helpful suggestions when appropriate
5. Confirm understanding of complex requirements
"""

# =============================================================================
# ERROR HANDLING PROMPTS
# =============================================================================

EXTRACTION_FALLBACK_PROMPT = """
The previous extraction attempt failed. Please try a simpler approach:
Extract only the most obvious, explicitly mentioned information from this message.
Return a simple JSON object with clear key-value pairs.
"""

QUESTION_FALLBACK = "What additional information would help complete your request?"

STEPS_FALLBACK = ["Continue gathering requirements", "Review and refine collected information"]

# =============================================================================
# PROMPT VALIDATION
# =============================================================================

def validate_prompt_length(prompt: str, max_length: int = 4000) -> str:
    """Validate and truncate prompt if too long"""
    if len(prompt) <= max_length:
        return prompt
    
    # Truncate but try to keep it coherent
    truncated = prompt[:max_length-100] + "...\n\nPlease focus on the most important aspects."
    return truncated

def add_safety_instructions(prompt: str) -> str:
    """Add safety instructions to prompts"""
    safety_note = """
Important: Only extract factual information explicitly mentioned by the user. 
Do not make assumptions or add information not provided.
"""
    return prompt + "\n" + safety_note

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

GENERIC_EXTRACTION_TEMPLATE = """
You are an expert at extracting structured information from user messages.

Current Data: {current_data}
User Message: "{message}"

Extract new or updated information from the message.
{extraction_fields}

{json_instruction}
"""

GENERIC_ANALYSIS_TEMPLATE = """
Analyze the following information and provide insights:

Data to Analyze: {data}
Analysis Context: {context}

{analysis_instructions}

{response_format}
"""

# =============================================================================
# VERSION INFO
# =============================================================================

BASE_PROMPTS_VERSION = "1.0.0"
LAST_UPDATED = "2025-07-19"