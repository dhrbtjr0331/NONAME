from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import END, StateGraph

from .base_agent import BaseAgent, AgentState
from app.models.rfq_assistant_schema import RfqDataSchema
from app.prompts.rfq_assistant import get_data_extraction_prompt, get_next_question_prompt, get_html_generation_prompt

from datetime import datetime

from xhtml2pdf import pisa
from io import BytesIO

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
        llm_model = self.llm.with_structured_output(RfqDataSchema)

        system_prompt = get_data_extraction_prompt(latest_message.content)

        try:
            # Invoke LLM to extract structured data
            extraction_result = await llm_model.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=latest_message.content)
            ])

            extracted_data = extraction_result.model_dump()
            print("EXTRACTED_DATA: ", extracted_data)

            # Update domain data with extracted values, but only for non-None values
            # This preserves existing data from previous messages
            for key, value in extracted_data.items():
                if value is not None:
                    state["domain_data"][key] = value

        except Exception as e:
            print(f"Error extracting RFQ data: {e}")
            # TODO: Handle extraction error (e.g., log, fallback, etc.)
        
        return state


    async def generate_response_node(self, state: AgentState) -> AgentState:
        """Generate response based on processed input - DOMAIN SPECIFIC"""
        
        # Extract latest message content
        for i in range(len(state["messages"]) - 1, -1, -1):
            if isinstance(state["messages"][i], HumanMessage):
                latest_message = state["messages"][i]
                break
        
        if not latest_message:
            return state
        
        # Get context of last ten messages
        context_window = self._get_context_window(state["messages"], window_size=10)

        # If no messages, return empty state
        if not context_window:
            state["messages"].append(AIMessage(content="I don't see your query. What would you like to know?"))
            return state

        system_prompt = get_next_question_prompt(state["domain_data"], context_window)
        
        # Generate response based on the current state
        try:
            # Invoke LLM to extract a response with next question
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=latest_message.content)
            ])
            
            state["messages"].append(AIMessage(content=response.content))

        except Exception as e:
            print(f"Error generating response: {e}")
            # Fallback response in case of error
            state["messages"].append(AIMessage(content="I'm here to assist you! What would you like to know?"))

        return state

    
    def generate_rfq_pdf_node(self, state: AgentState) -> AgentState:
        """Generate RFQ PDF document """
        
        try:
            rfq_data = state.get("domain_data", {})
            
            # Use LLM to generate HTML
            html_content = self._generate_html_with_llm(rfq_data)
            
            # Convert HTML to PDF
            pdf_bytes = self._html_to_pdf_bytes(html_content)
            
            filename = self._generate_pdf_filename(rfq_data)
        
            # Update domain_data with structured file info
            updated_domain_data = rfq_data.copy()
            updated_domain_data["rfq_pdf"] = {
                "content": pdf_bytes,
                "filename": filename,
                "content_type": "application/pdf",
                "size": len(pdf_bytes),
                "created_at": datetime.now().isoformat()
            }
            
            # TODO: DELETE THIS WHEN DONE TESTING Optional: Save PDF to file (for testing purposes)
            self._save_pdf_to_file(pdf_bytes, filename)
            
            # Add PDF generation success message
            state["messages"].append(AIMessage(content=f"RFQ PDF generated successfully: {filename}"))

            # Return updated state
            return {
                **state,
                "domain_data": updated_domain_data
            }
            
        except Exception as e:
            print(f"Error generating RFQ PDF: {str(e)}")
            # Return original state with error information
            return {
                **state,
                "domain_data": {
                    **state.get("domain_data", {}),
                    "pdf_generation_error": str(e)
                }
            }
    
    def has_full_schema(self, state: AgentState) -> str:
        """Check if the domain data contains all required fields"""
        required_fields = RfqDataSchema.model_fields.keys()
        
        data = state.get("domain_data", {})

        is_full = all(field in data and data[field] is not None for field in required_fields)
        if is_full:
            return "Full"
        else:
            return "Need more information"
        

    def build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""

        workflow = StateGraph(AgentState)
        
        # Add nodes - same workflow for all agents
        workflow.add_node("update_data", self.update_domain_data_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("generate_rfq_pdf", self.generate_rfq_pdf_node)
        
        # Add edges - same flow for all agents
        workflow.set_entry_point("update_data")
        workflow.add_conditional_edges(
            "update_data",
            self.has_full_schema,  # Check if domain data is complete
            {  # Name returned by route_joke : Name of next node to visit
                "Full": "generate_rfq_pdf",
                "Need more information": "generate_response",
            },
        )
        workflow.add_edge("generate_rfq_pdf", END)
        workflow.add_edge("generate_response", END)


        
        return workflow.compile(checkpointer=self.memory)
    

    def _generate_html_with_llm(self, rfq_data: Dict[str, Any]) -> str:
        system_prompt = get_html_generation_prompt(rfq_data)
        
        # Call your LLM here
        response = self.llm.invoke(system_prompt)
        return response.content


    def _html_to_pdf_bytes(self, html_content: str) -> bytes:
        """Convert HTML to PDF using xhtml2pdf"""
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)
        
        if not pdf.err:
            return result.getvalue()
        else:
            raise Exception("Error generating PDF")

    def _generate_pdf_filename(self, rfq_data: Dict[str, Any]) -> str:
        """
        Generate a filename for the RFQ PDF based on the data.
        
        Args:
            rfq_data: Dictionary containing RFQ information
            
        Returns:
            Generated filename string
        """
        # Get product name and clean it for filename
        product_name = rfq_data.get("product_name", "Product")
        clean_product_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_product_name = clean_product_name.replace(' ', '_')
        
        # Get current date
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Get RFQ ID if available
        rfq_id = rfq_data.get("rfq_id", "")
        
        # Build filename
        if rfq_id:
            filename = f"RFQ_{rfq_id}_{clean_product_name}_{date_str}.pdf"
        else:
            filename = f"RFQ_{clean_product_name}_{date_str}.pdf"
        
        return filename


    # Optional: Helper method to save PDF to file (for testing)
    def _save_pdf_to_file(self, pdf_bytes: bytes, filename: str = "rfq_document.pdf"):
        """Save PDF bytes to a file (useful for testing)"""
        with open(filename, "wb") as f:
            f.write(pdf_bytes)
        print(f"PDF saved to {filename}")

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