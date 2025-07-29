"""
Flow Overview:
1. RFQ Analysis & Planning (Workflow - Prompt Chaining)
2. Multi-channel Supplier Discovery (Workflow - Parallelization) 
3. Basic Supplier Evaluation & Scoring (Workflow - Orchestrator-Workers)
4. Final Supplier List Generation (Simple output formatting)
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import END, StateGraph

from .base_agent import BaseAgent, AgentState
from app.models.rfq_assistant_schema import RfqDataSchema
from app.prompts.rfq_assistant import get_data_extraction_prompt, get_next_question_prompt, get_html_generation_prompt

# GENERIC AgentState - works for ANY agent type
class AgentState(TypedDict):
    """Generic state for any LangGraph agent"""
    messages: List[BaseMessage]
    domain_data: Dict[str, Any]  # Generic domain data (could be RFQ, supplier info, etc.)
    user_id: Optional[str]
    session_id: str
    next_action: Optional[str]

class ResearchPhase(Enum):
    PLANNING = "planning"
    DISCOVERY = "discovery" 
    EVALUATION = "evaluation"
    COMPLETE = "complete"

class SupplierResearchAgent:
    """Supplier Research Agent using generic AgentState"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.agent_name = "Supplier Research Agent"
    
    def initialize_domain_data(self, rfq_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize domain_data with supplier research specific structure"""
        return {
            # Input data
            "rfq_data": rfq_data,
            
            # Research state
            "current_phase": ResearchPhase.PLANNING.value,
            "research_plan": None,
            
            # Discovery results
            "supplier_candidates": [],
            "search_results": {
                "database_results": [],
                "web_results": [],
                "directory_results": []
            },
            
            # Evaluation results
            "evaluated_suppliers": [],
            "supplier_scores": {},
            
            # Final output
            "potential_suppliers": [],  # [{"company_name": "ABC Corp", "location": "Detroit", "score": 8.5}]
            
            # Control flow
            "max_suppliers_to_find": 20,
            "target_suppliers": 10,
            "search_completed": {
                "databases": False,
                "web": False,
                "directories": False
            }
        }
    
    def build_graph(self):
        """Build the simplified research workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Phase 1: Analysis & Planning (Prompt Chaining)
        workflow.add_node("analyze_rfq", self.analyze_rfq_requirements)
        workflow.add_node("create_research_plan", self.create_research_plan)
        
        # Phase 2: Multi-channel Discovery (Parallelization)
        workflow.add_node("search_databases", self.search_supplier_databases)
        workflow.add_node("search_web", self.search_web_suppliers) 
        workflow.add_node("search_directories", self.search_industry_directories)
        workflow.add_node("consolidate_discoveries", self.consolidate_supplier_candidates)
        
        # Phase 3: Basic Evaluation (Orchestrator-Workers)
        workflow.add_node("evaluate_basic_fit", self.evaluate_basic_supplier_fit)
        workflow.add_node("score_suppliers", self.score_suppliers)
        
        # Phase 4: Final List Generation
        workflow.add_node("generate_supplier_list", self.generate_final_supplier_list)
        
        # Define the simplified flow
        workflow.set_entry_point("analyze_rfq")
        
        # Phase 1: Sequential analysis
        workflow.add_edge("analyze_rfq", "create_research_plan")
        
        # Phase 2: Parallel discovery
        workflow.add_edge("create_research_plan", "search_databases")
        workflow.add_edge("create_research_plan", "search_web")
        workflow.add_edge("create_research_plan", "search_directories")
        
        # Consolidate parallel results
        workflow.add_edge("search_databases", "consolidate_discoveries")
        workflow.add_edge("search_web", "consolidate_discoveries") 
        workflow.add_edge("search_directories", "consolidate_discoveries")
        
        # Phase 3: Basic evaluation workflow
        workflow.add_edge("consolidate_discoveries", "evaluate_basic_fit")
        workflow.add_edge("evaluate_basic_fit", "score_suppliers")
        
        # Phase 4: Final output
        workflow.add_edge("score_suppliers", "generate_supplier_list")
        
        workflow.set_finish_point("generate_supplier_list")
        
        return workflow.compile()

    # PHASE 1: ANALYSIS & PLANNING (Prompt Chaining Pattern)
    async def analyze_rfq_requirements(self, state: AgentState) -> AgentState:
        """Analyze RFQ to extract key supplier requirements"""
        
        # Extract RFQ data from domain_data
        rfq_data = state["domain_data"]["rfq_data"]
        
        # Use LLM to analyze RFQ and extract supplier requirements
        analysis_prompt = f"""
        Analyze this RFQ data and extract key supplier requirements:
        
        RFQ Data: {rfq_data}
        
        Extract:
        - Product/component specifications
        - Manufacturing processes needed
        - Required certifications
        - Geographic preferences
        - Quantity/volume requirements
        - Industry/application context
        - Key search keywords for supplier discovery
        
        Return structured analysis focusing on what type of suppliers we need to find.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert at analyzing RFQs for supplier research."),
                HumanMessage(content=analysis_prompt)
            ])
            
            # Store analysis results
            state["domain_data"]["rfq_analysis"] = response.content
            state["domain_data"]["current_phase"] = ResearchPhase.PLANNING.value
            
            # Add message for tracking
            state["messages"].append(AIMessage(content=f"RFQ analysis completed. Identified key supplier requirements."))
            
        except Exception as e:
            print(f"Error in RFQ analysis: {e}")
            state["messages"].append(AIMessage(content="Error analyzing RFQ requirements."))
        
        return state
    
    async def create_research_plan(self, state: AgentState) -> AgentState:
        """Create targeted research strategy based on RFQ analysis"""
        
        rfq_analysis = state["domain_data"].get("rfq_analysis", "")
        
        planning_prompt = f"""
        Based on this RFQ analysis, create a targeted supplier research plan:
        
        Analysis: {rfq_analysis}
        
        Create a research plan with:
        - Search keywords and terms
        - Relevant industry codes (NAICS, SIC)
        - Geographic search scope
        - Supplier database priorities
        - Manufacturing capability keywords
        - Certification requirements to search for
        
        Format as structured plan for systematic supplier discovery.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert at creating supplier research strategies."),
                HumanMessage(content=planning_prompt)
            ])
            
            # Store research plan
            state["domain_data"]["research_plan"] = response.content
            state["domain_data"]["current_phase"] = ResearchPhase.DISCOVERY.value
            
            state["messages"].append(AIMessage(content="Research plan created. Beginning supplier discovery."))
            
        except Exception as e:
            print(f"Error creating research plan: {e}")
            state["messages"].append(AIMessage(content="Error creating research plan."))
        
        return state

    # PHASE 2: DISCOVERY (Parallelization Pattern)
    async def search_supplier_databases(self, state: AgentState) -> AgentState:
        """Search structured supplier databases (ThomasNet, Alibaba, etc.)"""
        
        research_plan = state["domain_data"].get("research_plan", "")
        
        # Simulate database search (replace with actual API calls)
        try:
            # This would call actual supplier database APIs
            database_results = [
                {"company_name": "TechManufacturing Corp", "source": "ThomasNet", "location": "Michigan"},
                {"company_name": "Precision Industries", "source": "Alibaba", "location": "Ohio"},
                # ... more results
            ]
            
            state["domain_data"]["search_results"]["database_results"] = database_results
            state["domain_data"]["search_completed"]["databases"] = True
            
            state["messages"].append(AIMessage(content=f"Database search completed. Found {len(database_results)} potential suppliers."))
            
        except Exception as e:
            print(f"Error in database search: {e}")
            state["domain_data"]["search_completed"]["databases"] = True
        
        return state
    
    async def search_web_suppliers(self, state: AgentState) -> AgentState:
        """Web search for suppliers using targeted queries"""
        
        research_plan = state["domain_data"].get("research_plan", "")
        
        try:
            # This would use web search APIs
            web_results = [
                {"company_name": "Advanced Manufacturing LLC", "source": "Web", "website": "example.com"},
                {"company_name": "Quality Components Inc", "source": "Web", "website": "example2.com"},
                # ... more results
            ]
            
            state["domain_data"]["search_results"]["web_results"] = web_results
            state["domain_data"]["search_completed"]["web"] = True
            
            state["messages"].append(AIMessage(content=f"Web search completed. Found {len(web_results)} potential suppliers."))
            
        except Exception as e:
            print(f"Error in web search: {e}")
            state["domain_data"]["search_completed"]["web"] = True
        
        return state
    
    async def search_industry_directories(self, state: AgentState) -> AgentState:
        """Search industry-specific directories and associations"""
        
        research_plan = state["domain_data"].get("research_plan", "")
        
        try:
            # This would search industry directories
            directory_results = [
                {"company_name": "Industrial Solutions Co", "source": "Industry Directory", "certifications": ["ISO 9001"]},
                {"company_name": "Manufacturing Experts Ltd", "source": "Trade Association", "location": "Illinois"},
                # ... more results
            ]
            
            state["domain_data"]["search_results"]["directory_results"] = directory_results
            state["domain_data"]["search_completed"]["directories"] = True
            
            state["messages"].append(AIMessage(content=f"Directory search completed. Found {len(directory_results)} potential suppliers."))
            
        except Exception as e:
            print(f"Error in directory search: {e}")
            state["domain_data"]["search_completed"]["directories"] = True
        
        return state
    
    async def consolidate_supplier_candidates(self, state: AgentState) -> AgentState:
        """Merge and deduplicate suppliers from all sources"""
        
        # Wait for all searches to complete
        search_completed = state["domain_data"]["search_completed"]
        if not all(search_completed.values()):
            # Not all searches done yet, wait
            return state
        
        # Consolidate results from all sources
        all_results = []
        search_results = state["domain_data"]["search_results"]
        
        all_results.extend(search_results["database_results"])
        all_results.extend(search_results["web_results"])
        all_results.extend(search_results["directory_results"])
        
        # Simple deduplication by company name
        seen_companies = set()
        consolidated_suppliers = []
        
        for supplier in all_results:
            company_name = supplier["company_name"].lower().strip()
            if company_name not in seen_companies:
                seen_companies.add(company_name)
                consolidated_suppliers.append(supplier)
        
        state["domain_data"]["supplier_candidates"] = consolidated_suppliers
        state["domain_data"]["current_phase"] = ResearchPhase.EVALUATION.value
        
        state["messages"].append(AIMessage(content=f"Consolidated {len(consolidated_suppliers)} unique supplier candidates."))
        
        return state

    # PHASE 3: BASIC EVALUATION (Orchestrator-Workers Pattern)
    async def evaluate_basic_supplier_fit(self, state: AgentState) -> AgentState:
        """Evaluate each supplier against basic RFQ requirements"""
        
        supplier_candidates = state["domain_data"]["supplier_candidates"]
        rfq_data = state["domain_data"]["rfq_data"]
        
        evaluation_prompt = f"""
        Evaluate these supplier candidates against RFQ requirements:
        
        RFQ Requirements: {rfq_data}
        
        Supplier Candidates: {supplier_candidates}
        
        For each supplier, evaluate:
        - Geographic compatibility (0-10)
        - Manufacturing capability match (0-10)
        - Size/scale appropriateness (0-10)
        - Certification alignment (0-10)
        
        Return evaluation results with reasoning.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert at evaluating supplier fit for RFQs."),
                HumanMessage(content=evaluation_prompt)
            ])
            
            # Store evaluation results
            state["domain_data"]["supplier_evaluation"] = response.content
            
            state["messages"].append(AIMessage(content="Supplier evaluation completed."))
            
        except Exception as e:
            print(f"Error in supplier evaluation: {e}")
            state["messages"].append(AIMessage(content="Error evaluating suppliers."))
        
        return state
    
    async def score_suppliers(self, state: AgentState) -> AgentState:
        """Score suppliers based on multiple criteria"""
        
        supplier_evaluation = state["domain_data"].get("supplier_evaluation", "")
        supplier_candidates = state["domain_data"]["supplier_candidates"]
        
        scoring_prompt = f"""
        Based on this evaluation, assign numerical scores to each supplier:
        
        Evaluation: {supplier_evaluation}
        
        Create final scores (0-10) for each supplier considering:
        - Overall capability match
        - Geographic preference
        - Company reliability indicators
        - Information completeness
        
        Return suppliers with scores in JSON format.
        """
        
        try:
            # Use structured output for scoring
            llm_with_structure = self.llm.with_structured_output({
                "type": "object",
                "properties": {
                    "scored_suppliers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "company_name": {"type": "string"},
                                "score": {"type": "number"},
                                "reasoning": {"type": "string"}
                            }
                        }
                    }
                }
            })
            
            response = await llm_with_structure.ainvoke([
                SystemMessage(content="Score suppliers based on RFQ fit. Return structured JSON."),
                HumanMessage(content=scoring_prompt)
            ])
            
            state["domain_data"]["scored_suppliers"] = response["scored_suppliers"]
            
            state["messages"].append(AIMessage(content="Supplier scoring completed."))
            
        except Exception as e:
            print(f"Error scoring suppliers: {e}")
            # Fallback to simple scoring
            simple_scores = [{"company_name": s["company_name"], "score": 7.0, "reasoning": "Default score"} 
                           for s in supplier_candidates]
            state["domain_data"]["scored_suppliers"] = simple_scores
        
        return state

    # PHASE 4: FINAL OUTPUT
    async def generate_final_supplier_list(self, state: AgentState) -> AgentState:
        """Generate final list of potential suppliers"""
        
        scored_suppliers = state["domain_data"].get("scored_suppliers", [])
        target_suppliers = state["domain_data"]["target_suppliers"]
        
        # Sort by score (highest first) and limit to target number
        sorted_suppliers = sorted(scored_suppliers, key=lambda x: x["score"], reverse=True)
        final_suppliers = sorted_suppliers[:target_suppliers]
        
        state["domain_data"]["potential_suppliers"] = final_suppliers
        state["domain_data"]["current_phase"] = ResearchPhase.COMPLETE.value
        
        # Create summary message
        supplier_names = [s["company_name"] for s in final_suppliers]
        summary = f"Supplier research completed. Found {len(final_suppliers)} potential suppliers: {', '.join(supplier_names)}"
        
        state["messages"].append(AIMessage(content=summary))
        
        return state

# USAGE WITH GENERIC AgentState
async def find_suppliers_for_rfq(rfq_data: Dict[str, Any], session_id: str, user_id: str = None) -> Dict[str, Any]:
    """Main entry point using generic AgentState"""
    
    agent = SupplierResearchAgent(llm=your_llm_instance)
    graph = agent.build_graph()
    
    # Initialize generic state with supplier research domain data
    initial_state = AgentState(
        messages=[HumanMessage(content="Find suppliers for this RFQ")],
        domain_data=agent.initialize_domain_data(rfq_data),
        user_id=user_id,
        session_id=session_id,
        next_action=None
    )
    
    result = await graph.ainvoke(initial_state)
    
    # Extract results from domain_data
    return {
        "suppliers": result["domain_data"]["potential_suppliers"],
        "search_summary": result["messages"][-1].content,
        "session_id": session_id
    }
    # Example output:
    # {
    #   "suppliers": [
    #     {"company_name": "ABC Manufacturing", "score": 9.2, "reasoning": "Perfect capability match"},
    #     {"company_name": "XYZ Precision", "score": 8.7, "reasoning": "Strong capabilities"},
    #     ...
    #   ],
    #   "search_summary": "Found 10 potential suppliers: ABC Manufacturing, XYZ Precision, ...",
    #   "session_id": "supplier-search-123"
    # }# Supplier Research Agent - Simplified Architecture
