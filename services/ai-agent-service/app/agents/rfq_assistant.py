from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json

from .base_agent import BaseAgent, AgentState
from app.prompts.rfq_assistant import (
    SYSTEM_PROMPT,
    get_data_extraction_prompt,
    get_context_analysis_prompt,
    get_next_question_prompt,
    get_next_steps_prompt
)
from app.services.ai_providers.factory import get_llm_provider, get_extraction_llm

class RFQAssistant(BaseAgent):
    """RFQ-specific agent that inherits generic workflow from BaseAgent"""
    
    def __init__(self, llm=None):
        # Call parent with RFQ-specific info
        super().__init__("RFQ Assistant", "rfq", llm)
        
        # Create separate clean LLM instance for extraction tasks
        self.extraction_llm = get_extraction_llm()

    
    # IMPLEMENT ABSTRACT METHODS - RFQ-SPECIFIC
    
    async def process_user_input(self, state: AgentState) -> AgentState:
        """Process user input with intelligent RFQ context analysis"""
        if not state["messages"]:
            return state
        
        latest_message = state["messages"][-1]
        
        # Initialize domain_data if needed
        if "domain_data" not in state:
            state["domain_data"] = {}
        
        # Enhance state with intelligent context analysis
        await self._analyze_message_context(latest_message.content, state)
        

        return state
    
    async def _analyze_message_context(self, message: str, state: AgentState) -> None:
        """Use LLM to analyze message context and set appropriate flags"""
        context_prompt = get_context_analysis_prompt(message)
        
        try:
            # Separate context for analysis task using dedicated extraction LLM
            analysis_messages = [
                SystemMessage(content="You are a message analysis specialist. Analyze the provided message and return ONLY JSON format responses. Do not engage in conversation."),
                HumanMessage(content=context_prompt)
            ]
            context_result = await self.extraction_llm.ainvoke({"messages": analysis_messages})
            context_data = json.loads(context_result)
            
            # Update state with context insights
            if context_data.get("urgency"):
                state["domain_data"]["urgency"] = context_data["urgency"]
            if context_data.get("industry"):
                state["domain_data"]["industry_context"] = context_data["industry"]
            if context_data.get("stage"):
                state["domain_data"]["procurement_stage"] = context_data["stage"]
            if context_data.get("style"):
                state["domain_data"]["communication_style"] = context_data["style"]
            

        except Exception as e:
            # Fallback to simple urgency detection
            message_lower = message.lower()
            if any(word in message_lower for word in ["urgent", "asap", "rush", "immediately"]):
                state["domain_data"]["urgency"] = "high"
            print(f"⚠️ Context analysis failed, using fallback: {e}")
    
    async def update_domain_data(self, state: AgentState) -> AgentState:
        """Extract RFQ data from conversation - RFQ SPECIFIC"""
        
        if not state["messages"]:
            return state
        
        # Get the latest user message
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        
        if not user_messages:
            return state
        
        latest_user_message = user_messages[-1].content
        
        # LLM-POWERED RFQ DATA EXTRACTION
        extracted_rfq_data = await self._extract_rfq_data_with_llm(latest_user_message, state["domain_data"])
        
        # Update domain_data with RFQ-specific information
        if extracted_rfq_data:
            state["domain_data"].update(extracted_rfq_data)
            print(f"🔍 LLM Extracted RFQ data: {extracted_rfq_data}")
        
        return state
    
    def get_system_prompt_template(self):
        """Get RFQ-specific system prompt from centralized prompts"""
        return SYSTEM_PROMPT
    
    # RFQ-SPECIFIC HELPER METHODS
    
    async def _extract_rfq_data_with_llm(self, message: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to intelligently extract RFQ data from user message"""
        extraction_prompt = get_data_extraction_prompt(message, current_data)
        try:
            # Use LLM for intelligent extraction with CLEAR task-specific context
            
            # SIMPLIFIED: Direct extraction request with minimal prompt contamination
            simple_extraction_message = f"""TASK: Extract RFQ data from this message and return ONLY JSON format.

MESSAGE: "{message}"

EXTRACT: product names, quantities, timelines, budgets, specifications

RETURN ONLY JSON like: {{"product_name": "found product", "quantity": 123, "application": "use case"}}.

JSON:"""
            
            extraction_messages = [
                SystemMessage(content=extraction_prompt),
                HumanMessage(content=simple_extraction_message)
            ]
            
            extraction_result = await self.extraction_llm.ainvoke({"messages": extraction_messages})
            
            # Parse JSON response
            try:
                extracted_data = json.loads(extraction_result)
                if isinstance(extracted_data, dict):
                    return extracted_data
            except json.JSONDecodeError as json_err:
                # Fallback: try to find JSON in response
                import re
                json_match = re.search(r'\{.*\}', extraction_result, re.DOTALL)
                if json_match:
                    json_content = json_match.group()

                        extracted_data = json.loads(json_content)
                        if isinstance(extracted_data, dict):
                            return extracted_data
            return {}  # Fallback to empty if parsing fails
            
        except Exception as e:
            import traceback
            return {}  # Graceful fallback
    
    async def _determine_next_question_with_llm(self, rfq_data: Dict[str, Any], conversation_context: List[str]) -> str:
        """Use LLM to determine the most appropriate next question"""
        question_prompt = get_next_question_prompt(rfq_data, conversation_context)
        
        try:
            question = await self.llm.ainvoke({"messages": [SystemMessage(content=question_prompt)]})
            return question.strip().strip('"').strip("'")
        except Exception as e:
            print(f"⚠️ Next question generation failed: {e}")
            return "What additional information would help complete your RFQ?"
    
    async def get_rfq_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive RFQ summary from conversation history"""
        # Get full conversation history
        conversation_data = await self.get_conversation_history(session_id)
        
        if conversation_data["message_count"] == 0:
            return {
                "summary": "No conversation history found for this session.",
                "rfq_data": {},
                "conversation_length": 0,
                "session_id": session_id
            }
        
        # Get accumulated domain data
        existing_state = await self.get_session_state(session_id)
        rfq_data = existing_state.get("domain_data", {})
        
        # Generate summary
        summary_parts = []
        if rfq_data.get("product_name"):
            summary_parts.append(f"Product: {rfq_data['product_name']}")
        if rfq_data.get("quantity"):
            summary_parts.append(f"Quantity: {rfq_data['quantity']} units")
        if rfq_data.get("timeline"):
            summary_parts.append(f"Timeline: {rfq_data['timeline']}")
        if rfq_data.get("budget_range"):
            summary_parts.append(f"Budget: {rfq_data['budget_range']}")
        if rfq_data.get("urgency"):
            summary_parts.append(f"Urgency: {rfq_data['urgency']}")
        
        # Create conversation summary
        conversation_summary = []
        for msg in conversation_data["conversation"]:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_summary.append(f"{role}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
        
        summary_text = "RFQ Summary:\n" + "\n".join(f"• {part}" for part in summary_parts) if summary_parts else "No RFQ details collected yet."
        
        return {
            "summary": summary_text,
            "rfq_data": rfq_data,
            "conversation_summary": conversation_summary,
            "conversation_length": conversation_data["message_count"],
            "session_id": session_id,
            "next_steps": await self._suggest_next_steps_with_llm(rfq_data, conversation_data["message_count"])
        }
    
    async def _suggest_next_steps_with_llm(self, rfq_data: Dict[str, Any], conversation_length: int) -> List[str]:
        """Use LLM to intelligently suggest next steps"""
        steps_prompt = get_next_steps_prompt(rfq_data, conversation_length)
        
        try:
            steps_result = await self.llm.ainvoke({"messages": [SystemMessage(content=steps_prompt)]})
            
            # Parse JSON response
            try:
                steps_data = json.loads(steps_result)
                if isinstance(steps_data, list):
                    return [str(step) for step in steps_data]
            except json.JSONDecodeError:
                # Fallback: try to find JSON array in response
                import re
                json_match = re.search(r'\[.*\]', steps_result, re.DOTALL)
                if json_match:
                    steps_data = json.loads(json_match.group())
                    if isinstance(steps_data, list):
                        return [str(step) for step in steps_data]
                        
            # Fallback to simple steps if parsing fails
            return ["Continue gathering RFQ requirements", "Add more detailed specifications"]
            
        except Exception as e:
            print(f"⚠️ Next steps generation failed: {e}")
            return ["Continue refining RFQ requirements"]