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
    
    def __init__(self, agent_name: str, llm=None):
        self.agent_name = agent_name
        self.llm = llm
        self.memory = MemorySaver()
    
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