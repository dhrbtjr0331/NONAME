def get_rfq_analysis_prompt(rfq_data: str) -> str:
    """Generate a prompt for analyzing RFQ data to extract supplier requirements."""
    return f"""
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


def get_research_planning_prompt(rfq_analysis: str) -> str:
    """Generate a prompt for planning supplier research based on RFQ data and analysis."""
    return f"""
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


def get_supplier_evaluation_prompt(rfq_data: dict, supplier_candidates: list) -> str:
    return f"""
        Evaluate these supplier candidates against RFQ requirements:
        
        RFQ Requirements: {rfq_data}
        
        Supplier Candidates: {supplier_candidates}
        
        For each supplier, evaluate:
        - Geographic compatibility (0-100)
        - Manufacturing capability match (0-100)
        - Size/scale appropriateness (0-100)
        - Certification alignment (0-100)
        
        Return evaluation results with reasoning.
        """


def get_scoring_prompt(supplier_evaluation: str) -> str:
    return f"""
        Based on this evaluation, assign numerical scores to each supplier:
        
        Evaluation: {supplier_evaluation}
        
        Create final scores (0-100) for each supplier considering:
        - Overall capability match
        - Geographic preference
        - Company reliability indicators
        - Information completeness
        
        Return suppliers with scores in JSON format.
        """