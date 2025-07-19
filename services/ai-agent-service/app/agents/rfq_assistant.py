from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json
import re

from .base_agent import BaseAgent, AgentState

class RFQExtraction(BaseModel):
    """Structured RFQ data extraction"""
    product_name: str = Field(description="Name of the product being sourced")
    specifications: Dict[str, Any] = Field(description="Technical specifications")
    quantity: int = Field(description="Quantity needed", default=0)
    timeline: str = Field(description="Timeline for delivery")
    quality_requirements: str = Field(description="Quality standards required")
    budget_range: str = Field(description="Budget constraints")
    additional_notes: str = Field(description="Any additional requirements")

class RFQAssistant(BaseAgent):
    """AI Assistant specialized for helping manufacturers create detailed RFQs"""
    
    def __init__(self, llm=None):
        super().__init__("RFQ Assistant", llm)
        self.extraction_parser = JsonOutputParser(pydantic_object=RFQExtraction)
    
    def get_system_prompt_template(self) -> ChatPromptTemplate:
        """Get the specialized RFQ assistant prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert procurement assistant helping manufacturers create detailed Request for Quotations (RFQs). 

Your role is to:
1. Guide users through comprehensive RFQ creation
2. Ask clarifying questions to gather complete product specifications
3. Help define quality requirements and standards
4. Assist with quantity planning and timeline considerations
5. Suggest important details they might have missed

Current RFQ Data:
{rfq_data}

Guidelines:
- Be conversational and helpful
- Ask one focused question at a time
- Provide suggestions based on industry best practices
- Help users think through all aspects of their procurement needs
- Extract structured data when users provide information

Always aim to gather:
- Product name and detailed specifications
- Required quantities and timeline
- Quality standards and certifications needed
- Budget constraints or expectations
- Delivery terms and locations
- Any special requirements or constraints"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{messages}")
        ])
    
    async def process_user_input(self, state: AgentState) -> AgentState:
        """Process user input and extract RFQ information"""
        if not state["messages"]:
            return state
        
        latest_message = state["messages"][-1]
        
        # Try to extract structured RFQ data from the user's message
        extracted_data = await self._extract_rfq_data(latest_message.content, state["rfq_data"])
        
        # Update RFQ data with extracted information
        if extracted_data:
            state["rfq_data"].update(extracted_data)
        
        return state
    
    async def _extract_rfq_data(self, message: str, current_rfq_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured RFQ data from user message"""
        # Simple keyword-based extraction for now
        # In production, you'd use more sophisticated NLP/LLM-based extraction
        
        extracted = {}
        message_lower = message.lower()
        
        # Extract product name
        if "product" in message_lower or "component" in message_lower:
            # Simple regex to find product mentions
            product_match = re.search(r'(?:product|component|part|item)(?:\s+(?:is|called|named))?\s+([a-zA-Z0-9\s]+)', message_lower)
            if product_match:
                extracted["product_name"] = product_match.group(1).strip()
        
        # Extract quantity
        quantity_match = re.search(r'(\d+(?:,\d{3})*)\s*(?:units?|pieces?|pcs?|items?)', message_lower)
        if quantity_match:
            extracted["quantity"] = int(quantity_match.group(1).replace(',', ''))
        
        # Extract timeline keywords
        timeline_keywords = ["week", "month", "day", "asap", "urgent", "deadline"]
        for keyword in timeline_keywords:
            if keyword in message_lower:
                # Extract the context around the timeline mention
                timeline_match = re.search(rf'.{{0,20}}{keyword}.{{0,20}}', message_lower)
                if timeline_match:
                    extracted["timeline"] = timeline_match.group(0).strip()
                break
        
        # Extract budget information
        budget_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
        if budget_match:
            extracted["budget_range"] = f"${budget_match.group(1)}"
        
        return extracted
    
    def _determine_next_question(self, rfq_data: Dict[str, Any]) -> str:
        """Determine what question to ask next based on current RFQ data"""
        
        if not rfq_data.get("product_name"):
            return "What specific product or component are you looking to source?"
        
        if not rfq_data.get("specifications"):
            return f"Could you provide detailed specifications for the {rfq_data['product_name']}? For example, dimensions, materials, performance requirements, etc."
        
        if not rfq_data.get("quantity"):
            return "What quantity do you need? Please specify the number of units."
        
        if not rfq_data.get("timeline"):
            return "What's your timeline for this procurement? When do you need delivery?"
        
        if not rfq_data.get("quality_requirements"):
            return "What quality standards or certifications are required? Any specific testing or compliance requirements?"
        
        if not rfq_data.get("budget_range"):
            return "Do you have a target budget or price range in mind for this procurement?"
        
        # If we have most basic info, ask about additional details
        return "Are there any additional requirements, such as packaging specifications, delivery location preferences, or other special considerations?"
    
    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate AI response with RFQ-specific logic"""
        if not state["messages"]:
            welcome_msg = "Hello! I'm here to help you create a comprehensive RFQ. Let's start by understanding what you're looking to source. What product or component do you need?"
            state["messages"].append(AIMessage(content=welcome_msg))
            return state
        
        # Check if we should ask a specific follow-up question
        next_question = self._determine_next_question(state["rfq_data"])
        
        # Use the base class to generate a response
        state = await super().generate_response_node(state)
        
        # Add the next logical question if the AI didn't ask one
        if next_question and state["messages"]:
            last_response = state["messages"][-1].content
            if "?" not in last_response:  # If AI didn't ask a question, add our suggested one
                enhanced_response = f"{last_response}\n\n{next_question}"
                state["messages"][-1] = AIMessage(content=enhanced_response)
        
        return state
    
    def get_rfq_summary(self, rfq_data: Dict[str, Any]) -> str:
        """Generate a summary of the current RFQ data"""
        if not rfq_data:
            return "No RFQ information collected yet."
        
        summary_parts = []
        
        if rfq_data.get("product_name"):
            summary_parts.append(f"Product: {rfq_data['product_name']}")
        
        if rfq_data.get("quantity"):
            summary_parts.append(f"Quantity: {rfq_data['quantity']} units")
        
        if rfq_data.get("timeline"):
            summary_parts.append(f"Timeline: {rfq_data['timeline']}")
        
        if rfq_data.get("budget_range"):
            summary_parts.append(f"Budget: {rfq_data['budget_range']}")
        
        if rfq_data.get("quality_requirements"):
            summary_parts.append(f"Quality Requirements: {rfq_data['quality_requirements']}")
        
        return "Current RFQ Summary:\n" + "\n".join(f"• {part}" for part in summary_parts)