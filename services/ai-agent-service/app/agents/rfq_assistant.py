from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import END, StateGraph

from .base_agent import BaseAgent, AgentState
from app.models.rfq_assistant_schema import RfqDataSchema
from app.prompts.rfq_assistant import get_data_extraction_prompt


class RFQAssistant(BaseAgent):
    """RFQ-specific agent that inherits generic workflow from BaseAgent"""
    
    def __init__(self, llm=None):
        # Call parent with RFQ-specific info
        super().__init__("RFQ Assistant", llm)

    async def update_domain_data_node(self, state: AgentState) -> AgentState:
        """Extract and update domain-specific data - DOMAIN SPECIFIC"""

        # Extract latest message content
        for i in range(len(state["messages"]) - 1, -1, -1):
            if isinstance(state["messages"][i], HumanMessage):
                latest_message = state["messages"][i]
                break
        
        if not latest_message:
            return state
        
        # Initialize domain data if needed
        if "domain_data" not in state:
            state["domain_data"] = {}

        # Initialize llm model that provides structured output
        llm_model = self.llm.get_llm_with_structured_output(RfqDataSchema)

        system_prompt = get_data_extraction_prompt(latest_message.content, RfqDataSchema)

        try:
            # Invoke LLM to extract structured data
            extraction_result = await llm_model.ainvoke({
                "messages": [SystemMessage(content=system_prompt)]
            })
            extracted_data = extraction_result.model_dump()

            # Update domain data with extracted values
            state["domain_data"].update(extracted_data)

        except Exception as e:
            print(f"Error extracting RFQ data: {e}")
            # TODO: Handle extraction error (e.g., log, fallback, etc.)
        
        return state

    # TODO: currently a dummy node
    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate response based on processed input - DOMAIN SPECIFIC"""
        
        # Generate response based on the current state
        response_content = "Thank you for your RFQ. We will process it and get back to you shortly."
        
        # Create AI message with the response
        ai_message = AIMessage(content=response_content)
        
        # Append to messages
        state["messages"].append(ai_message)
        
        return state

    def build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""

        workflow = StateGraph(AgentState)
        
        # Add nodes - same workflow for all agents
        workflow.add_node("update_data", self.update_domain_data_node)
        workflow.add_node("generate_response", self.generate_response_node)
        
        # Add edges - same flow for all agents
        workflow.set_entry_point("update_data")
        workflow.add_edge("update_data", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile(checkpointer=self.memory)

    async def chat(self, message: str, session_id: str, domain_data: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """Main chat interface - SAME FOR ALL AGENTS"""
        graph = self.build_graph()
        
        # Get existing conversation history and state
        existing_state = await self.get_session_state(session_id)
        
        # Append new message to existing conversation
        all_messages = existing_state["messages"] + [HumanMessage(content=message)]
        
        # Merge domain data (new data takes precedence)
        merged_domain_data = existing_state["domain_data"].copy()
        if domain_data:
            merged_domain_data.update(domain_data)
        
        # Prepare state with full conversation history
        initial_state = AgentState(
            messages=all_messages,
            domain_data=merged_domain_data,
            user_id=user_id or existing_state["user_id"],
            session_id=session_id,
            next_action=None
        )
        
        # Run the graph
        config = {"configurable": {"thread_id": session_id}}
        result = await graph.ainvoke(initial_state, config=config)
        
        # Return structured response
        return {
            "response": result["messages"][-1].content if result["messages"] else "I'm here to help!",
            "domain_data": result["domain_data"],
            "session_id": session_id,
            "agent_type": self.agent_type,
            "message_count": len(result["messages"])
        }
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get existing session state from memory"""
        try:
            config = {"configurable": {"thread_id": session_id}}
            # Try to get existing state from the graph's memory
            graph = self.build_graph()
            existing_state = graph.get_state(config)
            
            if existing_state and existing_state.values:
                return {
                    "messages": existing_state.values.get("messages", []),
                    "domain_data": existing_state.values.get("domain_data", {}),
                    "user_id": existing_state.values.get("user_id"),
                    "agent_type": existing_state.values.get("agent_type", self.agent_type),
                    "next_action": existing_state.values.get("next_action", None),
                }
        except Exception:
            # If no existing state, return empty
            pass
        
        return {
            "messages": [],
            "domain_data": {},
            "user_id": None,
            "agent_name": self.agent_name,
            "next_action": None,
        }