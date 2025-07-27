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
    next_action: Optional[str]

session_memory = MemorySaver()

class BaseAgent(ABC):
    
    def __init__(self, agent_name: str, llm=None):
        self.agent_name = agent_name
        self.llm = llm
        self.memory = session_memory
    
    # ABSTRACT METHODS - Each agent MUST implement these
    @abstractmethod
    async def update_domain_data_node(self, state: AgentState) -> AgentState:
        """Extract and update domain-specific data - DOMAIN SPECIFIC"""
        pass

    @abstractmethod
    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate response based on processed input - DOMAIN SPECIFIC"""
        pass

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        pass

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
            "agent_name": self.agent_name,
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
                    "agent_name": existing_state.values.get("agent_name", self.agent_name),
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