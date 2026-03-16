import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.agents.state import AgentState
from app.agents.prompts import (
    FOUNDER_PROMPT, MARKET_VALIDATION_PROMPT, COMPETITOR_ANALYSIS_PROMPT,
    PRICING_STRATEGY_PROMPT, MVP_ARCHITECT_PROMPT, SKEPTIC_PROMPT
)
from app.agents.tools import serper_client, GLOBAL_VECTOR_STORE
from app.agents.llm_service import llm_service

def founder_node(state: AgentState):
    print("---FOUNDER AGENT---")
    idea = state['idea']
    
    analysis_id = state.get('analysis_id')
    
    if 'logs' not in state or state['logs'] is None:
        state['logs'] = []
    if 'trace' not in state or state['trace'] is None:
        state['trace'] = []
        
    messages = [
        SystemMessage(content=FOUNDER_PROMPT),
        HumanMessage(content=f"Startup Idea: {idea}")
    ]
    response = llm_service.invoke(messages)
    refined_idea = response.content
    
    state['refined_idea'] = refined_idea
    state['current_agent'] = "Founder Agent"
    state['logs'].append(f"Founder Result: {refined_idea[:100]}...")
    
    state['trace'].append({
        "agent": "Founder Agent",
        "step": "refine_idea",
        "model": "llama-3.3-70b-versatile",
        "prompt": [m.content for m in messages],
        "tool_calls": [],
        "llm_response": refined_idea
    })
    return state

def market_validation_node(state: AgentState):
    print("---MARKET AGENT---")
    short_idea = state.get('idea', '')
    refined_idea = state.get('refined_idea', '')
    
    query = f"{short_idea} market size trends growth"
    search_results = serper_client.search(query)
    snippets = [r.get('snippet', '') for r in search_results.get('organic', [])[:5]]
    
    tool_trace = {
        "tool": "serper",
        "query": query,
        "output": snippets
    }

    if snippets:
        GLOBAL_VECTOR_STORE.add_documents(
            snippets, 
            [{"source": "google_search", "agent": "market_validation", "doc_type": "market"}] * len(snippets), 
            analysis_id=state.get('analysis_id')
        )
    messages = [
        SystemMessage(content=MARKET_VALIDATION_PROMPT),
        HumanMessage(content=f"Idea: {refined_idea}\n\nSearch Data:\n{json.dumps(snippets)}")
    ]
    response = llm_service.invoke(messages)
    
    state['market_data'] = {"analysis": response.content, "raw_search": snippets}
    state['current_agent'] = "Market Validation Agent"
    state['logs'].append("Market Validation Complete")
    
    state['trace'].append({
        "agent": "Market Validation Agent",
        "step": "market_research",
        "model": "llama-3.3-70b-versatile",
        "prompt": [m.content for m in messages],
        "tool_calls": [tool_trace],
        "llm_response": response.content
    })
    return state

def competitor_analysis_node(state: AgentState):
    print("---COMPETITOR AGENT---")
    short_idea = state.get('idea', '')
    refined_idea = state.get('refined_idea', '')
    
    # 1. Search
    query = f"{short_idea} top competitors startups"
    search_results = serper_client.search(query)
    snippets = [r.get('snippet', '') for r in search_results.get('organic', [])[:5]]
    
    # Trace Tool Call
    tool_trace = {
        "tool": "serper",
        "query": query,
        "output": snippets
    }

    # 2. RAG (Store)
    if snippets:
        GLOBAL_VECTOR_STORE.add_documents(
            snippets, 
            [{"source": "google_search", "agent": "competitor_analysis", "doc_type": "competitor"}] * len(snippets), 
            analysis_id=state.get('analysis_id')
        )

    # 3. Analyze
    messages = [
        SystemMessage(content=COMPETITOR_ANALYSIS_PROMPT),
        HumanMessage(content=f"Idea: {refined_idea}\n\nCompatitor Data:\n{json.dumps(snippets)}")
    ]
    response = llm_service.invoke(messages)
    
    state['competitors'] = [{"analysis": response.content}]
    state['current_agent'] = "Competitor Analysis Agent"
    state['logs'].append("Competitor Analysis Complete")
    
    state['trace'].append({
        "agent": "Competitor Analysis Agent",
        "step": "competitor_analysis",
        "model": "llama-3.3-70b-versatile",
        "prompt": [m.content for m in messages],
        "tool_calls": [tool_trace],
        "llm_response": response.content
    })
    return state

def pricing_strategy_node(state: AgentState):
    print("---PRICING AGENT---")
    # Retrieve relevant pricing info
    # Retrieve relevant pricing info
    docs = GLOBAL_VECTOR_STORE.similarity_search(
        "pricing cost subscription price plan", 
        k=4, 
        analysis_id=state.get('analysis_id')
    )
    context = "\n".join([d.page_content for d in docs])
    
    messages = [
        SystemMessage(content=PRICING_STRATEGY_PROMPT),
        HumanMessage(content=f"Context from Knowledge Base:\n{context}\n\nCompetitor Analysis:\n{state['competitors'][0]['analysis']}")
    ]
    response = llm_service.invoke(messages)
    
    state['pricing_strategy'] = {"strategy": response.content, "benchmarks_used": [d.page_content[:50] for d in docs]}
    state['current_agent'] = "Pricing Strategy Agent"
    state['logs'].append("Pricing Strategy Complete")
    
    state['trace'].append({
        "agent": "Pricing Strategy Agent",
        "step": "pricing_analysis",
        "model": "llama-3.3-70b-versatile",
        "prompt": [m.content for m in messages],
        "tool_calls": [
            {"tool": "faiss_retrieval", "query": "pricing cost subscription price plan", "output": [d.page_content for d in docs]}
        ],
        "llm_response": response.content
    })
    return state

def mvp_architect_node(state: AgentState):
    print("---MVP AGENT---")
    # Feed previous decisions
    summary = f"""
    Refined Idea: {state['refined_idea']}
    Market: {state['market_data']['analysis']}
    Competitors: {state['competitors'][0]['analysis']}
    Pricing: {state['pricing_strategy']['strategy']}
    """
    
    messages = [
        SystemMessage(content=MVP_ARCHITECT_PROMPT),
        HumanMessage(content=f"Build the MVP Plan based on:\n{summary}")
    ]
    response = llm_service.invoke(messages)
    
    state['mvp_plan'] = {"plan": response.content}
    state['current_agent'] = "MVP Architect Agent"
    state['logs'].append("MVP Architecture Complete")
    
    state['trace'].append({
        "agent": "MVP Architect Agent",
        "step": "mvp_design",
        "model": "llama-3.3-70b-versatile",
        "prompt": [m.content for m in messages],
        "tool_calls": [],
        "llm_response": response.content
    })
    return state

def skeptic_node(state: AgentState):
    print("---SKEPTIC AGENT---")
    # Review everything
    summary = f"""
    Idea: {state['refined_idea']}
    Market: {state['market_data']['analysis']}
    Competitors: {state['competitors'][0]['analysis']}
    MVP: {state['mvp_plan']['plan']}
    """
    
    # Retrieve relevant supporting evidence for critique
    relevant_docs = GLOBAL_VECTOR_STORE.similarity_search(
        f"potential risks challenges downsides {state['refined_idea']}", 
        k=2, 
        analysis_id=state.get('analysis_id')
    )
    rag_context = "\n".join([d.page_content for d in relevant_docs])

    messages = [
        SystemMessage(content=SKEPTIC_PROMPT),
        HumanMessage(content=f"Critique this:\n{summary}\n\nReference Context (Potential Risks):\n{rag_context}")
    ]
    response = llm_service.invoke(messages)
    
    state['skeptic_critique'] = response.content
    state['current_agent'] = "Skeptic Agent"
    state['logs'].append("Skeptic Review Complete")
    
    state['trace'].append({
        "agent": "Skeptic Agent",
        "step": "critique",
        "model": "llama-3.3-70b-versatile",
        "prompt": [m.content for m in messages],
        "tool_calls": [
            {"tool": "faiss_retrieval", "query": f"potential risks challenges downsides {state['refined_idea']}", "output": [d.page_content for d in relevant_docs]}
        ],
        "llm_response": response.content
    })
    return state