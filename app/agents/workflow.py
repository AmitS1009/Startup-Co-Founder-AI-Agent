from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    founder_node,
    market_validation_node,
    competitor_analysis_node,
    pricing_strategy_node,
    mvp_architect_node,
    skeptic_node
)

def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("founder", founder_node)
    workflow.add_node("market_validation", market_validation_node)
    workflow.add_node("competitor_analysis", competitor_analysis_node)
    workflow.add_node("pricing_strategy", pricing_strategy_node)
    workflow.add_node("mvp_architect", mvp_architect_node)
    workflow.add_node("skeptic", skeptic_node)
    
    # Define Edges / Flow
    # Founder -> Market Validation -> Competitor Analysis -> Pricing Strategy -> MVP Architect -> Skeptic
    workflow.set_entry_point("founder")
    workflow.add_edge("founder", "market_validation")
    workflow.add_edge("market_validation", "competitor_analysis")
    workflow.add_edge("competitor_analysis", "pricing_strategy")
    workflow.add_edge("pricing_strategy", "mvp_architect")
    workflow.add_edge("mvp_architect", "skeptic")
    workflow.add_edge("skeptic", END)
    
    return workflow.compile()
