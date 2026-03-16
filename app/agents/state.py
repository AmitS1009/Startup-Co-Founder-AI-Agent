from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    idea: str
    refined_idea: Optional[str]
    market_data: Optional[Dict[str, Any]]
    competitors: Optional[List[Dict[str, Any]]]
    pricing_strategy: Optional[Dict[str, Any]]
    mvp_plan: Optional[Dict[str, Any]]
    skeptic_critique: Optional[str]
    
    analysis_id: str
    user_id: Optional[int]

    # Internal state
    logs: List[str] # Log of interactions for UI
    trace: List[Dict[str, Any]] # Detailed execution trace
    current_agent: str
