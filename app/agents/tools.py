import os
import requests
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.config import settings

class SerperClient:
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.url = "https://google.serper.dev/search"

    def search(self, query: str, type: str = "search"):
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(self.url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

class VectorStoreManager:
    def __init__(self):
        # Using HuggingFace MiniLM for embeddings (Runs locally)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None

    def add_documents(self, texts: list[str], metadatas: list[dict], analysis_id: str):
        if not analysis_id:
            raise ValueError("analysis_id is required for adding documents")
            
        # Inject analysis_id and ensure safe metadata
        for m in metadatas:
            m['analysis_id'] = analysis_id
                
        documents = [
            Document(page_content=t, metadata=m) for t, m in zip(texts, metadatas)
        ]
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4, analysis_id: str = None, doc_type: str = None):
        """
        Safely retrieves documents filtering by analysis_id manually to ensure isolation.
        """
        if not self.vector_store:
            return []
        if not analysis_id:
            raise ValueError("analysis_id is required for similarity search")

        # Fetch more candidates to allow for manual post-filtering (Safety)
        # We fetch k*5 to ensure we have enough after filtering
        docs = self.vector_store.similarity_search(query, k=k*5) 
        
        filtered_docs = []
        for doc in docs:
            # Manual Safety Check
            if doc.metadata.get('analysis_id') != analysis_id:
                continue
            
            # Optional: Filter by doc_type if provided
            if doc_type and doc.metadata.get('doc_type') != doc_type:
                continue
                
            filtered_docs.append(doc)
            if len(filtered_docs) >= k:
                break
                
        return filtered_docs


serper_client = SerperClient()
GLOBAL_VECTOR_STORE = VectorStoreManager()

