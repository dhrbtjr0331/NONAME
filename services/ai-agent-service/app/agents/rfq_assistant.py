from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
import re

from .base_agent import BaseAgent, AgentState

class RFQAssistant(BaseAgent):
    """RFQ-specific agent that inherits generic workflow from BaseAgent"""
    
    def __init__(self, llm=None):
        # Call parent with RFQ-specific info
        super().__init__("RFQ Assistant", "rfq", llm)
    
    # IMPLEMENT ABSTRACT METHODS - RFQ-SPECIFIC
    
    async def process_user_input(self, state: AgentState) -> AgentState:
        """Process user input - RFQ SPECIFIC logic"""
        if not state["messages"]:
            return state
        
        # RFQ-specific preprocessing could go here
        # For example: detect if user is asking about pricing, specifications, etc.
        latest_message = state["messages"][-1]
        
        # Add RFQ-specific context to the state
        if "domain_data" not in state:
            state["domain_data"] = {}
        
        # RFQ-specific analysis
        message_lower = latest_message.content.lower()
        if any(word in message_lower for word in ["urgent", "asap", "rush"]):
            state["domain_data"]["urgency"] = "high"
        
        return state
    
    async def update_domain_data(self, state: AgentState) -> AgentState:
        """Extract RFQ data from conversation - RFQ SPECIFIC"""
        if not state["messages"]:
            return state
        
        # Get the latest user message
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            return state
        
        latest_user_message = user_messages[-1].content
        
        # RFQ-SPECIFIC DATA EXTRACTION
        extracted_rfq_data = self._extract_rfq_data(latest_user_message, state["domain_data"])
        
        # Update domain_data with RFQ-specific information
        if extracted_rfq_data:
            state["domain_data"].update(extracted_rfq_data)
            print(f"🔍 Extracted RFQ data: {extracted_rfq_data}")
        
        return state
    
    def get_system_prompt_template(self):
        """RFQ-specific system prompt"""
        return """You are an expert RFQ (Request for Quotation) assistant. 
        Help manufacturers create detailed procurement requests by gathering:
        - Product specifications
        - Quantities needed
        - Timeline requirements
        - Quality standards
        - Budget constraints
        
        Ask one focused question at a time and be conversational."""
    
    # RFQ-SPECIFIC HELPER METHODS
    
    def _extract_rfq_data(self, message: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured RFQ data from user message"""
        extracted = {}
        message_lower = message.lower()
        
        # Extract product name
        if any(keyword in message_lower for keyword in ["steel brackets", "brackets"]):
            extracted["product_name"] = "steel brackets"
        elif "product" in message_lower:
            # More sophisticated extraction could go here
            product_match = re.search(r'(?:product|component|part|item)(?:\s+(?:is|called|named))?\s+([a-zA-Z0-9\s]+)', message_lower)
            if product_match:
                extracted["product_name"] = product_match.group(1).strip()
        
        # Extract quantity
        quantity_match = re.search(r'(\d+(?:,\d{3})*)\s*(?:units?|pieces?|pcs?|items?)', message_lower)
        if quantity_match:
            extracted["quantity"] = int(quantity_match.group(1).replace(',', ''))
        
        # Extract timeline
        if "weeks" in message_lower:
            weeks_match = re.search(r'(\d+)\s*weeks?', message_lower)
            if weeks_match:
                extracted["timeline"] = f"{weeks_match.group(1)} weeks"
        
        # Extract budget
        budget_match = re.search(r'\$(\d+(?:,\d{3})*)', message)
        if budget_match:
            extracted["budget_range"] = f"${budget_match.group(1)}"
        
        return extracted
    
    def _determine_next_question(self, rfq_data: Dict[str, Any]) -> str:
        """Determine what RFQ question to ask next"""
        if not rfq_data.get("product_name"):
            return "What specific product or component are you looking to source?"
        
        if not rfq_data.get("quantity"):
            return "What quantity do you need?"
        
        if not rfq_data.get("timeline"):
            return "What's your target timeline for delivery?"
        
        if not rfq_data.get("budget_range"):
            return "Do you have a budget range in mind?"
        
        return "Are there any additional requirements we should include?"
    
    def get_rfq_summary(self, rfq_data: Dict[str, Any]) -> str:
        """Generate RFQ summary"""
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
        
        return "Current RFQ Summary:\n" + "\n".join(f"• {part}" for part in summary_parts)