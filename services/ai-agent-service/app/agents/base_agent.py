from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
import uuid
from datetime import datetime

# GENERIC AgentState - works for ANY agent type
class AgentState(TypedDict):
    """Generic state for any LangGraph agent"""
    messages: List[BaseMessage]
    domain_data: Dict[str, Any]  # Generic domain data (could be RFQ, supplier info, etc.)
    user_id: Optional[str]
    session_id: str
    agent_type: str  # "rfq", "supplier", "quote_analyzer", etc.
    next_action: Optional[str]

class BaseAgent(ABC):
    """Truly generic base class for ALL agents"""
    
    def __init__(self, agent_name: str, agent_type: str, llm=None):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.llm = llm
        self.memory = MemorySaver()
        self.message_history = {}
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat message history for session"""
        if session_id not in self.message_history:
            self.message_history[session_id] = ChatMessageHistory()
        return self.message_history[session_id]
    
    # ABSTRACT METHODS - Each agent MUST implement these
    @abstractmethod
    async def process_user_input(self, state: AgentState) -> AgentState:
        """Process user input - DOMAIN SPECIFIC"""
        pass
    
    @abstractmethod
    async def update_domain_data(self, state: AgentState) -> AgentState:
        """Extract and update domain-specific data - DOMAIN SPECIFIC"""
        pass
    
    @abstractmethod
    def get_system_prompt_template(self):
        """Get agent-specific prompt template - DOMAIN SPECIFIC"""
        pass
    
    # CONCRETE METHODS - Same for all agents
    def build_graph(self) -> StateGraph:
        """Build LangGraph workflow - SAME FOR ALL AGENTS"""
        workflow = StateGraph(AgentState)
        
        # Add nodes - same workflow for all agents
        workflow.add_node("process_input", self.process_user_input)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("update_data", self.update_domain_data)
        
        # Add edges - same flow for all agents
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "generate_response")
        workflow.add_edge("generate_response", "update_data")
        workflow.add_edge("update_data", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate AI response - SAME FOR ALL AGENTS"""
        # Get the latest user message
        latest_message = state["messages"][-1] if state["messages"] else None
        if not latest_message:
            state["messages"].append(AIMessage(content="I'm here to help! What would you like to know?"))
            return state
        
        # Prepare input for the LLM
        llm_input = {
            "messages": [latest_message],
            "domain_data": state["domain_data"],
            "user_id": state["user_id"],
            "agent_type": state["agent_type"]
        }
        
        # Generate response using the agent's LLM
        response = await self.llm.ainvoke(llm_input)
        
        # Add AI response to messages
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    async def chat(self, message: str, session_id: str, domain_data: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """Main chat interface - SAME FOR ALL AGENTS"""
        graph = self.build_graph()
        
        # Prepare initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            domain_data=domain_data or {},
            user_id=user_id,
            session_id=session_id,
            agent_type=self.agent_type,
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
            "agent_type": self.agent_type
        }