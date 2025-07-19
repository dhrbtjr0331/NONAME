from typing import Dict, Any, List, AsyncGenerator, Union, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import asyncio
import random

class MockLLM(LLM):
    """Mock LLM for testing RFQ assistant without external API calls"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rfq_responses = {
            "greeting": [
                "Hello! I'm here to help you create a comprehensive RFQ. What product are you looking to source?",
                "Hi there! Let's work together to build a detailed Request for Quotation. What can I help you with today?",
                "Welcome! I'll guide you through creating a professional RFQ. What product or service do you need to procure?"
            ],
            "product_inquiry": [
                "Great! Could you provide more specific details about the {product}? What are the key specifications I should know about?",
                "That sounds interesting. What are the technical requirements or specifications for the {product}?",
                "Perfect! To help suppliers provide accurate quotes, what specifications should I include for the {product}?"
            ],
            "quantity_follow_up": [
                "Good to know you need {quantity} units. What's your target timeline for delivery?",
                "Thanks for the quantity information. When do you need these {quantity} units delivered?",
                "With {quantity} units needed, what's your preferred delivery schedule?"
            ],
            "timeline_follow_up": [
                "Understood - {timeline} timeline. What quality standards or certifications are required for this procurement?",
                "That timeline works. Are there any specific quality requirements or industry standards we should mention?",
                "Got it on the timeline. What level of quality assurance do you need from suppliers?"
            ],
            "budget_inquiry": [
                "Do you have a target budget range in mind? This helps suppliers provide more relevant proposals.",
                "What's your budget expectation for this procurement? Even a rough range helps.",
                "Are there any budget constraints I should mention in the RFQ?"
            ],
            "additional_requirements": [
                "Are there any special packaging, shipping, or handling requirements?",
                "Do you need any specific certifications, warranties, or after-sales support?",
                "Are there any additional technical requirements or preferences we should include?"
            ],
            "summary": [
                "Let me summarize what we've gathered so far for your RFQ...",
                "Here's what we have for your Request for Quotation:",
                "Based on our conversation, here's your RFQ summary:"
            ],
            "completion": [
                "Your RFQ looks comprehensive! Would you like me to suggest any additional details?",
                "Great job! This RFQ should give suppliers all the information they need to provide accurate quotes.",
                "Excellent! Your RFQ covers all the essential details. Ready to send it out to suppliers?"
            ]
        }
    
    @property
    def _llm_type(self) -> str:
        return "mock_rfq_llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Generate mock response based on prompt content"""
        return self._generate_contextual_response(prompt)
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Async version of _call"""
        # Simulate some processing time
        await asyncio.sleep(0.5)
        return self._generate_contextual_response(prompt)
    
    def _generate_contextual_response(self, prompt: str) -> str:
        """Generate contextually appropriate response based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Extract any RFQ data from the prompt
        rfq_data = self._extract_rfq_context(prompt)
        
        # Determine response category based on prompt content and RFQ data
        if not rfq_data.get("product_name") and ("hello" in prompt_lower or "help" in prompt_lower):
            return random.choice(self.rfq_responses["greeting"])
        
        elif "product" in prompt_lower or "component" in prompt_lower:
            product = rfq_data.get("product_name", "your product")
            response = random.choice(self.rfq_responses["product_inquiry"])
            return response.format(product=product)
        
        elif rfq_data.get("quantity") and not rfq_data.get("timeline"):
            quantity = rfq_data["quantity"]
            response = random.choice(self.rfq_responses["quantity_follow_up"])
            return response.format(quantity=quantity)
        
        elif rfq_data.get("timeline") and not rfq_data.get("quality_requirements"):
            timeline = rfq_data["timeline"]
            response = random.choice(self.rfq_responses["timeline_follow_up"])
            return response.format(timeline=timeline)
        
        elif not rfq_data.get("budget_range") and ("budget" in prompt_lower or "price" in prompt_lower or "cost" in prompt_lower):
            return random.choice(self.rfq_responses["budget_inquiry"])
        
        elif "summary" in prompt_lower or "summarize" in prompt_lower:
            return random.choice(self.rfq_responses["summary"])
        
        elif self._is_rfq_complete(rfq_data):
            return random.choice(self.rfq_responses["completion"])
        
        else:
            # Default to asking for additional requirements
            return random.choice(self.rfq_responses["additional_requirements"])
    
    def _extract_rfq_context(self, prompt: str) -> Dict[str, Any]:
        """Extract RFQ context data from prompt"""
        # This is a simplified extraction - in reality, the RFQ data
        # would be passed more explicitly through the agent state
        rfq_data = {}
        
        # Look for RFQ data markers in the prompt
        if '"rfq_data":' in prompt:
            # Try to extract JSON-like RFQ data
            import re
            import json
            try:
                # Simple extraction of JSON-like data
                json_match = re.search(r'"rfq_data":\s*({[^}]*})', prompt)
                if json_match:
                    rfq_data = json.loads(json_match.group(1))
            except:
                pass
        
        return rfq_data
    
    def _is_rfq_complete(self, rfq_data: Dict[str, Any]) -> bool:
        """Check if RFQ has most essential information"""
        required_fields = ["product_name", "quantity", "timeline"]
        return all(rfq_data.get(field) for field in required_fields)

def get_mock_llm() -> MockLLM:
    """Factory function to create mock LLM instance"""
    MockLLM.model_rebuild()  # Rebuild the model to fix Pydantic issues
    return MockLLM()