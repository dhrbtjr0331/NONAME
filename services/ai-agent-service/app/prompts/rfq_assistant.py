"""
RFQ Assistant Prompts Collection

This file contains all prompts used by the RFQ Assistant agent for:
- System prompts
- Data extraction prompts  
- Context analysis prompts
- Question generation prompts
- Next steps analysis prompts

Centralizing prompts here makes them easier to:
- Maintain and update
- Version control
- A/B test different versions
- Reuse across similar agents
"""

# =============================================================================
# SYSTEM PROMPT - Core agent personality and instructions
# =============================================================================

SYSTEM_PROMPT = """You are an expert RFQ (Request for Quotation) assistant with deep knowledge of B2B procurement.

Your role is to help manufacturers create comprehensive, actionable RFQs by intelligently gathering:

🎯 CORE REQUIREMENTS:
- Product specifications and technical details
- Precise quantities and units
- Timeline and delivery requirements  
- Budget ranges and payment terms
- Quality standards and certifications
- Industry-specific compliance needs

🧠 APPROACH:
- Ask intelligent follow-up questions based on user context
- Recognize industry terminology and technical specifications
- Suggest relevant requirements the user might not have considered
- Adapt questioning style to user expertise level
- Focus on gathering actionable, procurement-ready information

💬 CONVERSATION STYLE:
- Be conversational and consultative
- Ask ONE focused question at a time
- Build on previous answers intelligently
- Offer helpful suggestions when appropriate
- Confirm understanding of complex requirements

Remember: Your goal is creating RFQs that will attract quality supplier responses."""

# =============================================================================
# DATA EXTRACTION PROMPTS
# =============================================================================

def get_data_extraction_prompt(message: str, current_data: dict) -> str:
    """Generate prompt for extracting RFQ data from user message"""
    from .base import format_data_for_prompt, format_json_instruction
    
    current_data_str = format_data_for_prompt(current_data, "Current RFQ Data")
    
    extraction_fields = """Extract ANY new or updated RFQ information from the user message. Look for:
- Product/component names and specifications
- Quantities (numbers with units)  
- Timeline/delivery requirements
- Budget/price ranges
- Quality standards/certifications
- Urgency indicators
- Technical specifications
- Industry/application context

Use these field names in your JSON response:
- product_name: specific product/component name
- quantity: numeric quantity
- quantity_unit: unit (pieces, tons, etc.)
- timeline: delivery timeframe
- budget_range: budget/price information
- specifications: technical specs
- quality_standards: quality requirements
- urgency: urgency level (high/medium/low)
- application: intended use/industry
- additional_requirements: other specific needs"""
    
    json_instruction = format_json_instruction(extraction_fields)
    
    return f"""You are an expert at extracting RFQ (Request for Quotation) information from user messages.

{current_data_str}
New User Message: "{message}"

{json_instruction}"""

# =============================================================================
# CONTEXT ANALYSIS PROMPTS
# =============================================================================

def get_context_analysis_prompt(message: str) -> str:
    """Generate prompt for analyzing message context and user signals"""
    return f"""Analyze this user message for RFQ context and urgency signals.

Message: "{message}"

Identify:
1. Urgency level (high/medium/low)
2. Industry context (manufacturing, automotive, electronics, etc.)
3. Procurement stage (early exploration, ready to purchase, etc.)
4. Communication style (technical, casual, formal)

Return JSON with detected context:
{{
  "urgency": "high/medium/low",
  "industry": "detected industry or null",
  "stage": "exploration/specification/ready_to_buy",
  "style": "technical/casual/formal"
}}"""

# =============================================================================
# QUESTION GENERATION PROMPTS
# =============================================================================

def get_next_question_prompt(rfq_data: dict, conversation_context: list) -> str:
    """Generate prompt for determining the best next question to ask"""
    context_str = "\n".join(conversation_context[-6:]) if conversation_context else "No previous conversation"
    
    return f"""You are an expert RFQ assistant. Based on the current RFQ data and conversation context, determine the BEST next question to ask.

Current RFQ Data:
{rfq_data}

Recent Conversation Context:
{context_str}

RFQ Completion Checklist:
- Product/component name and specifications
- Quantity and units
- Delivery timeline
- Budget/price expectations  
- Quality standards or certifications
- Technical specifications
- Intended application/industry
- Special requirements

Guidelines:
1. Ask about the MOST IMPORTANT missing information first
2. Be conversational and natural
3. Ask only ONE focused question
4. If most info is collected, ask about refinements or additional needs
5. Don't repeat questions already answered

Return ONLY the next question to ask (no explanation):"""

# =============================================================================
# NEXT STEPS ANALYSIS PROMPTS
# =============================================================================

def get_next_steps_prompt(rfq_data: dict, conversation_length: int) -> str:
    """Generate prompt for suggesting actionable next steps"""
    return f"""Analyze this RFQ data and suggest actionable next steps for the user.

RFQ Data:
{rfq_data}

Conversation Length: {conversation_length} messages

Provide 2-5 specific, actionable next steps. Consider:
- What critical information is still missing?
- Is the RFQ ready for supplier outreach?
- What refinements or clarifications are needed?
- Should they add technical specifications?
- Are there industry-specific considerations?

Return a JSON array of strings, each being a specific next step.
Example: ["Add technical specifications for material grade", "Specify quality certifications required", "Ready to publish RFQ to suppliers"]

JSON Response:"""

# =============================================================================
# SUMMARY GENERATION PROMPTS
# =============================================================================

def get_summary_generation_prompt(rfq_data: dict, conversation_summary: list) -> str:
    """Generate prompt for creating comprehensive RFQ summary"""
    conversation_str = "\n".join(conversation_summary) if conversation_summary else "No conversation history"
    
    return f"""Generate a comprehensive, professional RFQ summary based on the collected data and conversation.

Collected RFQ Data:
{rfq_data}

Conversation Summary:
{conversation_str}

Create a well-structured summary that includes:
1. Product/component overview
2. Quantity and specifications
3. Timeline and delivery requirements
4. Quality standards and compliance needs
5. Budget considerations (if provided)
6. Special requirements or notes

Format the summary as a professional RFQ document that suppliers can easily understand and respond to.

Professional RFQ Summary:"""

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_rfq_data_for_prompt(rfq_data: dict) -> str:
    """Format RFQ data for inclusion in prompts"""
    if not rfq_data:
        return "No RFQ data collected yet."
    
    formatted = []
    for key, value in rfq_data.items():
        if value:
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    return "\n".join(formatted) if formatted else "No RFQ data collected yet."

# =============================================================================
# PROMPT VERSIONING
# =============================================================================

PROMPT_VERSION = "1.0.0"
LAST_UPDATED = "2025-07-19"

# Future: Could add different versions for A/B testing
# SYSTEM_PROMPT_V2 = "..."
# DATA_EXTRACTION_PROMPT_V2 = "..."