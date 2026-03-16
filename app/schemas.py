from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class AnalysisRequest(BaseModel):
    idea: str

class AnalysisResponse(BaseModel):
    id: int
    idea: str
    result: Optional[Any] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
