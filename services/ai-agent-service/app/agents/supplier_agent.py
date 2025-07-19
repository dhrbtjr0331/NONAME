from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
import re

from .base_agent import BaseAgent, AgentState

""" NEED MODIFICATION."""

class SupplierAgent(BaseAgent):
    """Supplier analysis agent - DIFFERENT domain, SAME workflow"""
    
    def __init__(self, llm=None):
        # Call parent with Supplier-specific info
        super().__init__("Supplier Assistant", "supplier", llm)
    
    # IMPLEMENT ABSTRACT METHODS - SUPPLIER-SPECIFIC
    
    async def process_user_input(self, state: AgentState) -> AgentState:
        """Process user input - SUPPLIER SPECIFIC logic"""
        if not state["messages"]:
            return state
        
        # Supplier-specific preprocessing
        latest_message = state["messages"][-1]
        
        if "domain_data" not in state:
            state["domain_data"] = {}
        
        # Supplier-specific analysis
        message_lower = latest_message.content.lower()
        if any(word in message_lower for word in ["certified", "iso", "quality"]):
            state["domain_data"]["quality_focus"] = True
        
        return state
    
    async def update_domain_data(self, state: AgentState) -> AgentState:
        """Extract supplier data from conversation - SUPPLIER SPECIFIC"""
        if not state["messages"]:
            return state
        
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            return state
        
        latest_user_message = user_messages[-1].content
        
        # SUPPLIER-SPECIFIC DATA EXTRACTION
        extracted_supplier_data = self._extract_supplier_data(latest_user_message, state["domain_data"])
        
        if extracted_supplier_data:
            state["domain_data"].update(extracted_supplier_data)
            print(f"🏭 Extracted Supplier data: {extracted_supplier_data}")
        
        return state
    
    def get_system_prompt_template(self):
        """Supplier-specific system prompt"""
        return """You are a supplier evaluation assistant. 
        Help manufacturers analyze and compare suppliers by gathering:
        - Supplier capabilities and certifications
        - Production capacity and lead times
        - Quality standards and track record
        - Pricing and payment terms
        - Geographic location and logistics
        
        Ask focused questions to evaluate supplier suitability."""
    
    # SUPPLIER-SPECIFIC HELPER METHODS
    
    def _extract_supplier_data(self, message: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract supplier information from user message"""
        extracted = {}
        message_lower = message.lower()
        
        # Extract supplier name
        if "supplier" in message_lower:
            supplier_match = re.search(r'supplier\s+(?:is\s+)?([a-zA-Z0-9\s&]+)', message_lower)
            if supplier_match:
                extracted["supplier_name"] = supplier_match.group(1).strip()
        
        # Extract certifications
        cert_keywords = ["iso", "certified", "certification", "compliant"]
        if any(keyword in message_lower for keyword in cert_keywords):
            extracted["has_certifications"] = True
        
        # Extract capacity information
        capacity_match = re.search(r'(\d+(?:,\d{3})*)\s*(?:units?|pieces?)\s*(?:per|\/)\s*(?:month|week|day)', message_lower)
        if capacity_match:
            extracted["production_capacity"] = capacity_match.group(0)
        
        return extracted
    
    def get_supplier_summary(self, supplier_data: Dict[str, Any]) -> str:
        """Generate supplier evaluation summary"""
        if not supplier_data:
            return "No supplier information collected yet."
        
        summary_parts = []
        if supplier_data.get("supplier_name"):
            summary_parts.append(f"Supplier: {supplier_data['supplier_name']}")
        if supplier_data.get("has_certifications"):
            summary_parts.append("Certifications: Yes")
        if supplier_data.get("production_capacity"):
            summary_parts.append(f"Capacity: {supplier_data['production_capacity']}")
        
        return "Supplier Evaluation Summary:\n" + "\n".join(f"• {part}" for part in summary_parts)