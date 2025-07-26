from typing import Dict, Any, List
import asyncio
import random
import json
import re

class SimpleMockLLM:
    """Simple mock LLM that doesn't inherit from LangChain base classes"""
    
    def __init__(self):
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
    
    async def ainvoke(self, inputs: Dict[str, Any], config: Dict[str, Any] = None) -> str:
        """Async invoke method that LangChain expects"""
        # Simulate processing time
        await asyncio.sleep(0.3)
        
        # Extract the prompt from inputs
        if isinstance(inputs, dict):
            if "messages" in inputs:
                # Handle messages format
                messages = inputs["messages"]
                if isinstance(messages, list) and len(messages) > 0:
                    prompt = str(messages[-1])  # Get the latest message
                else:
                    prompt = str(messages)
            else:
                prompt = str(inputs)
        else:
            prompt = str(inputs)
        
        return self._generate_contextual_response(prompt, inputs)
    
    def invoke(self, inputs: Dict[str, Any], config: Dict[str, Any] = None) -> str:
        """Sync invoke method"""
        return asyncio.run(self.ainvoke(inputs, config))
    
    def _generate_contextual_response(self, prompt: str, full_inputs: Dict[str, Any] = None) -> str:
        """Generate contextually appropriate response based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Extract any RFQ data from the inputs
        rfq_data = {}
        if full_inputs and isinstance(full_inputs, dict):
            if "rfq_data" in full_inputs:
                rfq_data = full_inputs.get("rfq_data", {})
            else:
                # Try to extract from the prompt itself
                rfq_data = self._extract_rfq_context(prompt)
        
        # Determine response category based on prompt content and RFQ data
        if not rfq_data.get("product_name") and ("hello" in prompt_lower or "help" in prompt_lower or "rfq" in prompt_lower):
            return random.choice(self.rfq_responses["greeting"])
        
        elif any(keyword in prompt_lower for keyword in ["product", "component", "steel", "brackets", "sourcing"]):
            product = rfq_data.get("product_name", "your product")
            if "steel brackets" in prompt_lower:
                product = "steel brackets"
            response = random.choice(self.rfq_responses["product_inquiry"])
            return response.format(product=product)
        
        elif any(keyword in prompt_lower for keyword in ["1000", "units", "quantity"]):
            quantity = "1000"
            response = random.choice(self.rfq_responses["quantity_follow_up"])
            return response.format(quantity=quantity)
        
        elif any(keyword in prompt_lower for keyword in ["weeks", "timeline", "delivery", "6 weeks"]):
            timeline = "6 weeks"
            response = random.choice(self.rfq_responses["timeline_follow_up"])
            return response.format(timeline=timeline)
        
        elif any(keyword in prompt_lower for keyword in ["budget", "price", "cost", "$5000", "5000"]):
            return random.choice(self.rfq_responses["budget_inquiry"])
        
        elif "summary" in prompt_lower or "summarize" in prompt_lower:
            return random.choice(self.rfq_responses["summary"])
        
        elif self._is_conversation_complete(prompt_lower):
            return random.choice(self.rfq_responses["completion"])
        
        else:
            # Default to asking for additional requirements
            return random.choice(self.rfq_responses["additional_requirements"])
    
    def _extract_rfq_context(self, prompt: str) -> Dict[str, Any]:
        """Extract RFQ context data from prompt"""
        rfq_data = {}
        
        # Simple keyword extraction
        if "steel brackets" in prompt.lower():
            rfq_data["product_name"] = "steel brackets"
        
        quantity_match = re.search(r'(\d+)\s*units?', prompt.lower())
        if quantity_match:
            rfq_data["quantity"] = int(quantity_match.group(1))
        
        if "weeks" in prompt.lower():
            weeks_match = re.search(r'(\d+)\s*weeks?', prompt.lower())
            if weeks_match:
                rfq_data["timeline"] = f"{weeks_match.group(1)} weeks"
        
        budget_match = re.search(r'\$(\d+)', prompt)
        if budget_match:
            rfq_data["budget_range"] = f"${budget_match.group(1)}"
        
        return rfq_data
    
    def _is_conversation_complete(self, prompt_lower: str) -> bool:
        """Check if conversation seems to be wrapping up"""
        completion_keywords = ["done", "complete", "finished", "ready", "send", "finalize"]
        return any(keyword in prompt_lower for keyword in completion_keywords)

def get_simple_mock_llm() -> SimpleMockLLM:
    """Factory function to create simple mock LLM instance"""
    return SimpleMockLLM()