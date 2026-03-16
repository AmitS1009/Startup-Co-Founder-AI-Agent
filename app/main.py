from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db, engine, Base
from app.schemas import AnalysisRequest, AnalysisResponse
from app.db.models import Analysis 
from app.agents.workflow import create_workflow
from app.agents.state import AgentState
import uvicorn
import json

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Startup Co-Founder API")

workflow_app = create_workflow()

from fastapi.responses import StreamingResponse
import json
import asyncio

@app.post("/analyze")
async def analyze_idea(
    request: AnalysisRequest, 
    db: Session = Depends(get_db)
):
    import uuid
    analysis_id = str(uuid.uuid4())
    
    initial_state: AgentState = {
        "idea": request.idea,
        "refined_idea": None,
        "market_data": None,
        "competitors": None,
        "pricing_strategy": None,
        "mvp_plan": None,
        "skeptic_critique": None,
        "logs": ["Starting analysis..."],
        "current_agent": "Founder",
        "analysis_id": analysis_id,
        "user_id": 1  # Dummy or simply null.
    }

    async def event_generator():
        final_state = initial_state        
        try:
            for output in workflow_app.stream(initial_state):
                for key, value in output.items():
                    if isinstance(value, dict):
                        final_state.update(value)

                    # Check for trace updates to infer tool usage
                    if isinstance(value, dict) and "trace" in value and value["trace"]:
                        last_trace = value["trace"][-1]
                        agent_name = last_trace.get("agent")
                        tool_calls = last_trace.get("tool_calls", [])

                        if tool_calls:
                            model_name = last_trace.get("model", "Unknown Model")   
                            for tool in tool_calls:
                                tool_name = tool.get("tool")
                                tool_msg = f"🔧 {agent_name} used {tool_name}..." 
                                yield json.dumps({"type": "tool_use", "message": tool_msg, "model": model_name}) + "\n"                                             
                                
                                if tool_name == "serper":
                                     yield json.dumps({"type": "rag_op", "message": f"💾 {agent_name} embedding results...", "model": model_name}) + "\n"         
                        
                        if "Pricing" in agent_name:
                             model_name = last_trace.get("model", "Unknown Model")  
                             yield json.dumps({"type": "rag_op", "message": f"📤 {agent_name} retrieving context...", "model": model_name}) + "\n"                
                             
                    # Extract model from trace for the step completion too
                    model_for_step = "Unknown Model"
                    if isinstance(value, dict) and "trace" in value and value["trace"]:
                        model_for_step = value["trace"][-1].get("model", "Unknown Model")                                                                           
                    
                    yield json.dumps({"step": key, "details": "Agent finished", "model": model_for_step}) + "\n"                                                    
            
            result_data = {
                "idea": final_state.get('idea'),
                "refined_idea": final_state.get('refined_idea'),
                "market_data": final_state.get('market_data'),
                "competitors": final_state.get('competitors'),
                "pricing_strategy": final_state.get('pricing_strategy'),
                "mvp_plan": final_state.get('mvp_plan'),
                "skeptic_critique": final_state.get('skeptic_critique'),
                "trace": final_state.get('trace')
            }

            try:
                new_analysis = Analysis(
                    idea=request.idea,
                    result=result_data
                )
                db.add(new_analysis)
                db.commit()
                db.refresh(new_analysis)

                yield json.dumps({"type": "complete", "result": result_data}) + "\n"
            except Exception as e:
                yield json.dumps({"type": "error", "message": "DB Error: " + str(e)}) + "\n"
        except Exception as graph_err:
            import traceback
            traceback.print_exc()
            yield json.dumps({"type": "error", "message": "Workflow Error: " + str(graph_err)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/history", response_model=list[AnalysisResponse])
def get_history(
    db: Session = Depends(get_db)
):
    return db.query(Analysis).order_by(Analysis.created_at.desc()).all()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
