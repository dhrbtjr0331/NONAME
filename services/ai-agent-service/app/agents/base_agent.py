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

class BaseAgent(ABC):
    """Truly generic base class for ALL agents"""
    
    def __init__(self, agent_name: str, agent_type: str, llm=None):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.llm = llm
        self.memory = MemorySaver()
    
    
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
    
    def _get_context_window(self, messages: List[BaseMessage], window_size: int = 10) -> List[BaseMessage]:
        """Get the last N messages for context window"""
        if not messages:
            return []
        
        # Always include system message if it exists at the beginning
        system_messages = [msg for msg in messages[:1] if isinstance(msg, SystemMessage)]
        
        # Get the last window_size messages (excluding system messages from count)
        non_system_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
        recent_messages = non_system_messages[-window_size:] if len(non_system_messages) > window_size else non_system_messages
        
        # Combine: system message(s) first, then recent conversation
        return system_messages + recent_messages

    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate AI response with conversation context - SAME FOR ALL AGENTS"""
        if not state["messages"]:
            state["messages"].append(AIMessage(content="I'm here to help! What would you like to know?"))
            return state
        
        # Get conversation context window (last 10 messages + system messages)
        context_messages = self._get_context_window(state["messages"], window_size=10)
        
        # Add system prompt if not already present
        if not any(isinstance(msg, SystemMessage) for msg in context_messages):
            system_prompt = self.get_system_prompt_template()
            context_messages.insert(0, SystemMessage(content=system_prompt))
        
        # Prepare input for the LLM with full context
        llm_input = {
            "messages": context_messages,
            "domain_data": state["domain_data"],
            "user_id": state["user_id"],
            "agent_type": self.agent_type,
            "context_window_size": len(context_messages)
        }
        
        # Generate response using the agent's LLM
        response = await self.llm.ainvoke(llm_input)
        
        # Add AI response to messages
        state["messages"].append(AIMessage(content=response))
        
        return state
    
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
            "agent_type": self.agent_type,
            "next_action": None,
        }

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
    
    async def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Get full conversation history for a session"""
        existing_state = await self.get_session_state(session_id)
        
        # Convert messages to readable format
        conversation = []
        for msg in existing_state["messages"]:
            if hasattr(msg, 'content'):
                role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                conversation.append({
                    "role": role,
                    "content": msg.content,
                    "timestamp": getattr(msg, 'timestamp', None)
                })
        
        return {
            "session_id": session_id,
            "agent_type": existing_state["agent_type"],
            "conversation": conversation,
            "domain_data": existing_state["domain_data"],
            "message_count": len(conversation)
        }