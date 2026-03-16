# 🚀 Startup Co-Founder AI Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=langchain)]()
[![Groq](https://img.shields.io/badge/Groq_API-F55036?style=for-the-badge&logo=groq)]()

**AI Startup Co-Founder** is an advanced, autonomous multi-agent system designed to transform raw startup ideas into comprehensive, validated business plans. 

Built for performance and scale, the system orchestrates a complex workflow of specialized AI agents using **LangGraph** and **LangChain**. It leverages the ultra-fast **Groq API** (powered by `Llama-3.3-70b-versatile`) to perform high-level creative reasoning and deep analytical tasks. By integrating **Serper API** for real-time web research and a **FAISS** vector store for robust **Retrieval-Augmented Generation (RAG)**, the agents ground their business, market, and competitor analyses in real-world data.

This project demonstrates expertise in agentic workflows, production-ready backend engineering, state management, and real-time frontend integration.

---

## 🎯 Key Features & Agent Workflow

The system employs a collaborative multi-agent architecture where distinct personas tackle different facets of business planning:

1. 🧠 **Founder Agent**: Clarifies and refines the core startup vision.
2. 🌍 **Market Validation Agent**: Conducts live web research to analyze market size, trends, and growth potential.
3. 🕵️ **Competitor Analysis Agent**: Identifies top competitors and benchmarks the startup against them using real-world data constraints.
4. 💰 **Pricing Strategy Agent**: Synthesizes market and competitor data (via RAG) to formulate a viable monetization strategy.
5. 🏗️ **MVP Architect Agent**: Consolidates all previous insights to outline a strict, actionable Minimum Viable Product (MVP).
6. ⚖️ **Skeptic Agent**: Retrieves potential risks from the vector store to rigorously stress-test and critique the entire business plan.

### 🌟 Technical Highlights
- **Live Execution Streaming**: Watch agents think, research, and communicate in real-time through the frontend.
- **Trace Visualization**: Inspect granular flowcharts of agent thoughts, prompts, tool calls, and LLM responses.
- **Data Isolation**: Strict, ID-based context isolation per analysis within the FAISS vector database.
- **Persistent History**: Stores user sessions, logs, and generated reports securely in **PostgreSQL**.

## 🛠️ Tech Stack

- **Application Logic**: LangGraph, LangChain, FAISS
- **Backend**: FastAPI, Pydantic, SQLAlchemy 
- **Frontend**: Streamlit
- **LLM Engine**: Llama-3.3-70b-versatile (via **Groq API**)
- **Database**: PostgreSQL (Locally or via Supabase)
- **External Tools**: Serper API (Google Search), HuggingFace MiniLM (Embeddings)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database (Local or Supabase connection string)
- **Groq API Key**: Get one at [console.groq.com](https://console.groq.com)
- **Serper API Key**: Get one at [serper.dev](https://serper.dev)

### Setup Instructions

1. **Clone the repository & create environment:**
   ```bash
   git clone <repo-url>
   cd cofounder-agent
   cp .env.example .env
   ```

2. **Configure your `.env` file:**
   Populate your keys in the `.env` file. It should look like this:
   ```env
   GROQ_API_KEY=your_groq_api_key
   SERPER_API_KEY=your_serper_key
   DATABASE_URL=postgresql://user:pass@localhost/db
   SECRET_KEY=your_super_secret_key
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To experience the full platform, run the backend and frontend simultaneously.

**1. Start the FastAPI Backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

**2. Start the Streamlit UI (in a separate terminal):**
```bash
streamlit run ui/app.py
```

## 💻 Usage

1. Navigate to the Streamlit URL (typically `http://localhost:8501`).
2. **Register/Login** to your account.
3. Enter an initial, unstructured startup idea (e.g., "A platform for remote workers to find dog-friendly cafes").
4. Click **"Analyze"** and watch the real-time execution trace as the autonomous agents build your business plan from scratch!
