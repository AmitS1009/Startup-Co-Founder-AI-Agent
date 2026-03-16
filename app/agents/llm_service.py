from langchain_groq import ChatGroq
from app.config import settings

llm_service = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.LLM_MODEL,
    temperature=0.2
)
