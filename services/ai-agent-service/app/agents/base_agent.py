from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
import uuid
from datetime import datetime

class AgentState(TypedDict):
    """State for LangGraph agent"""
    messages: List[BaseMessage]
    rfq_data: Dict[str, Any]
    user_id: Optional[str]
    session_id: str
    next_action: Optional[str]

class RFQAgentResponse(TypedDict):
    """Structured response from RFQ agent"""
    message: str
    rfq_updates: Dict[str, Any]
    suggested_actions: List[str]
    confidence_score: float

class BaseAgent(ABC):
    """Base class for LangChain-powered AI agents"""
    
    def __init__(self, agent_name: str, llm=None):
        self.agent_name = agent_name
        self.llm = llm
        self.memory = MemorySaver()  # LangGraph checkpoint for conversation memory
        self.message_history = {}  # Store chat histories per session
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat message history for session using LangChain"""
        if session_id not in self.message_history:
            self.message_history[session_id] = ChatMessageHistory()
        return self.message_history[session_id]
    
    @abstractmethod
    def get_system_prompt_template(self) -> ChatPromptTemplate:
        """Get the prompt template for this agent"""
        pass
    
    @abstractmethod
    async def process_user_input(self, state: AgentState) -> AgentState:
        """Process user input and update state"""
        pass
    
    def create_chain_with_history(self):
        """Create a chain with message history using LangChain"""
        prompt = self.get_system_prompt_template()
        
        chain = prompt | self.llm | StrOutputParser()
        
        return RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="messages",
            history_messages_key="chat_history",
        )
    
    def build_graph(self) -> StateGraph:
        """Build LangGraph state graph for agent workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_input", self.process_user_input)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("update_rfq", self.update_rfq_node)
        
        # Add edges
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "generate_response")
        workflow.add_edge("generate_response", "update_rfq")
        workflow.add_edge("update_rfq", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate AI response using LLM"""
        # Get the latest user message
        latest_message = state["messages"][-1] if state["messages"] else None
        if not latest_message:
            state["messages"].append(AIMessage(content="I'm here to help! What would you like to know?"))
            return state
        
        # Prepare input for the LLM
        llm_input = {
            "messages": [latest_message],
            "rfq_data": state["rfq_data"],
            "user_id": state["user_id"]
        }
        
        # Generate response
        response = await self.llm.ainvoke(llm_input)
        
        # Add AI response to messages
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    async def update_rfq_node(self, state: AgentState) -> AgentState:
        """Update RFQ data based on conversation"""
        # This is where we'd extract structured data from the conversation
        # and update the RFQ fields
        
        # For now, this is a placeholder - we'll implement extraction logic
        return state
    
    async def chat(self, message: str, session_id: str, rfq_data: Dict[str, Any] = None, user_id: str = None) -> Dict[str, Any]:
        """Main chat interface"""
        graph = self.build_graph()
        
        # Prepare initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            rfq_data=rfq_data or {},
            user_id=user_id,
            session_id=session_id,
            next_action=None
        )
        
        # Run the graph
        config = {"configurable": {"thread_id": session_id}}
        result = await graph.ainvoke(initial_state, config=config)
        
        # Return structured response
        return {
            "response": result["messages"][-1].content if result["messages"] else "I'm here to help!",
            "rfq_updates": result["rfq_data"],
            "session_id": session_id
        }