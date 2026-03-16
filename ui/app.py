import streamlit as st
import requests
import json
import time
import textwrap
import streamlit.components.v1 as components
# --- PAGE CONFIG (Must be first) ---
st.set_page_config(page_title="AI Startup Co-Founder", page_icon="🚀", layout="wide")

# --- CONFIG ---
API_BASE_URL = "http://localhost:8000"

def analyze(idea):
    res = requests.post(f"{API_BASE_URL}/analyze", json={"idea": idea})
    if res.status_code == 200:
        return res.json()
    return None

def get_history():
    try:
        res = requests.get(f"{API_BASE_URL}/history")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []


# --- STYLES ---
# Custom CSS for "Premium" look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #1c2e2e;
        border: 1px solid #2e4e4e;
    }
    .agent-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #262730;
        margin-bottom: 0.5rem;
        border-left: 5px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'current_result' not in st.session_state:
    st.session_state.current_result = None

# --- MAIN APP ---
def main():
    st.title("🚀 AI Startup Co-Founder")
    
    # Main App
    with st.sidebar:
        if st.button("➕ New Analysis"):
            st.session_state.current_result = None
            st.rerun()
        
        st.header("📜 History")
        history = get_history()
        if isinstance(history, list):
            try:
                for item in history:
                    if not isinstance(item, dict):
                        continue
                    idea_text = item.get('idea') or "Untitled Analysis"
                    # Truncate idea for button label
                    label = (idea_text[:30] + '...') if len(idea_text) > 30 else idea_text
                    if st.button(f"📅 {label}", key=f"hist_{item.get('id')}"):
                        st.session_state.current_result = item.get('result')
                        # Helper: Inject idea if not in result (for old records)
                        if st.session_state.current_result and isinstance(st.session_state.current_result, dict):
                            st.session_state.current_result['idea'] = item.get('idea')
                        st.rerun()
            except Exception as e:
                st.error(f"Error loading history item: {e}")
        else:
            st.caption("Unable to load history.")

    # Input Area (only if no result selected)
    if not st.session_state.current_result:
        idea_input = st.text_area("What is your startup idea?", height=150, placeholder="e.g. Uber for dog walking...")
        
        if st.button("Analyze Idea 🚀"):
            if not idea_input:
                st.warning("Please enter an idea.")
                return
            
            # Progress UI
            progress_container = st.container()
            
            with progress_container:
                # st.info("Initiating AI Agents cluster...")
                
                with st.status("Agents working on your idea...", expanded=True) as status:
                    st.write("🚀 Initializing workflow...")
                    
                    # Streaming request
                    try:
                        response = requests.post(f"{API_BASE_URL}/analyze", json={"idea": idea_input}, stream=True)
                    except requests.exceptions.ConnectionError:
                        st.error("Backend Server is not running! Please start it with `uvicorn app.main:app --port 8000`.")
                        st.stop()
                    
                    final_result = None
                    
                    if response.status_code == 200:
                        # Container for live updates
                        live_log = st.container()
                        
                        try:
                            for line in response.iter_lines():
                                if line:
                                    try:
                                        decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line
                                        msg = json.loads(decoded_line)
                                        
                                        with live_log:
                                            if msg.get("type") == "tool_use":
                                                model = msg.get("model", "Unknown")
                                                st.markdown(f"""
                                                    <div style="margin-left: 20px; font-size: 0.9em; color: #aaa;">
                                                        <span style="color: #4ebecce0;">🔧 Tool:</span> {msg.get('message')} 
                                                        <span style="font-family: monospace; background: #333; padding: 2px 5px; border-radius: 4px; font-size: 0.8em; margin-left: 10px;">{model}</span>
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                                
                                            elif msg.get("type") == "rag_op":
                                                model = msg.get("model", "Unknown")
                                                st.markdown(f"""
                                                    <div style="margin-left: 20px; font-size: 0.9em; color: #aaa;">
                                                        <span style="color: #4ecc8ae0;">💾 RAG:</span> {msg.get('message')}
                                                        <span style="font-family: monospace; background: #333; padding: 2px 5px; border-radius: 4px; font-size: 0.8em; margin-left: 10px;">{model}</span>
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                                    
                                            if "step" in msg:
                                                step_name = msg["step"]
                                                model = msg.get("model", "Unknown")
                                                    
                                                labels = {
                                                        "founder": "🧠 Founder Agent",
                                                        "market_validation": "📊 Market Validation",
                                                        "competitor_analysis": "🏢 Competitor Analysis",
                                                        "pricing_strategy": "💸 Pricing Strategy",
                                                        "mvp_architect": "🛠️ MVP Architect",
                                                        "skeptic": "🖤 Skeptic Agent"
                                                    }
                                                display_name = labels.get(step_name, step_name)
                                                    
                                                st.markdown(f"""
                                                    <div style="background: #262730; border: 1px solid #4a4a4a; padding: 10px; border-radius: 8px; margin-top: 5px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                                                        <span style="font-weight: bold; font-size: 1.1em; color: #fff;">{display_name}</span>
                                                        <span style="font-family: monospace; background: #111; color: #00e0ff; padding: 4px 8px; border-radius: 6px; border: 1px solid #00e0ff40;">🤖 {model}</span>
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                            
                                            if msg.get("type") == "complete":
                                                final_result = msg.get("result")
                                            
                                            if msg.get("type") == "error":
                                                st.error(f"Error: {msg.get('message')}")
                                                
                                    except Exception as e:
                                        print(e)
                        
                        except requests.exceptions.ChunkedEncodingError:
                            st.error('Backend streaming ended abruptly! Ensure backend is running and model fits in memory.')
                        status.update(label="Analysis Complete! ✅", state="complete", expanded=False)
                    else:
                        st.error(f"Request failed with status {response.status_code}")
                    st.session_state.current_result = final_result
                    st.rerun()
    
    # Result Display (if result selected)
    if st.session_state.current_result:
        data = st.session_state.current_result
        
        # Show Title
        st.markdown(f"## 🚀 {data.get('idea', 'Project Analysis')}")
        
        # Create tabs for Results and Debug Trace
        result_tab, trace_tab = st.tabs(["📊 Analysis Results", "🐛 Execution Trace"])
        
        with result_tab:
            st.divider()
            st.header("Refined Concept")
            st.info(data.get('refined_idea'))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Market Data")
                m_data = data.get('market_data', {})
                if isinstance(m_data, dict):
                    st.markdown(m_data.get('analysis'))
                else:
                    st.write(m_data)

                st.subheader("🏢 Competitors")
                c_data = data.get('competitors', [{}])
                if c_data and isinstance(c_data, list):
                    c_data = c_data[0]
                
                if isinstance(c_data, dict):
                    st.markdown(c_data.get('analysis'))
                else:
                    st.write(c_data)

            with col2:
                st.subheader("💸 Pricing Strategy")
                p_data = data.get('pricing_strategy', {})
                st.markdown(p_data.get('strategy'))
                
                st.subheader("🛠️ MVP Plan")
                mvp_data = data.get('mvp_plan', {})
                mvp_content = mvp_data.get('plan')
                
                # Try to parse as JSON for pretty printing with built-in wrap support
                try:
                    if isinstance(mvp_content, str):
                        json_obj = json.loads(mvp_content)
                        st.json(json_obj)
                    else:
                        st.write(mvp_content) # st.write/markdown wraps text better than st.code
                except:
                    # Fallback to markdown for wrapping
                    st.markdown(mvp_content)

            st.subheader("🖤 Skeptic's Verdict")
            st.error(data.get('skeptic_critique'))
            
        with trace_tab:
            st.subheader("Process Workflow Visualization")
            trace = data.get('trace', [])
            
            if trace:
                # CSS Styles
                # ---------- TRACE VISUALIZATION FIX ----------
                flow_css = """
                <style>
                .flow-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                    margin-bottom: 40px;
                    font-family: Inter, sans-serif;
                }
                .agent-node {
                    background: linear-gradient(145deg, #262730, #2d2e38);
                    border: 1px solid #4a4a4a;
                    border-radius: 12px;
                    width: 100%;
                    max-width: 600px;
                    overflow: hidden;
                }
                .agent-header {
                    background: rgba(255, 75, 75, 0.1);
                    padding: 12px 20px;
                    display: flex;
                    justify-content: space-between;
                }
                .agent-title {
                    font-weight: 700;
                    color: #ff4b4b;
                }
                .model-badge {
                    font-family: monospace;
                    color: #00e0ff;
                }
                .substep-container {
                    padding: 15px 20px;
                }
                .substep-item {
                    display: flex;
                    gap: 12px;
                    margin-bottom: 10px;
                }
                .substep-icon {
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    background: #333;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .substep-text {
                    font-size: 0.9em;
                }
                .connector {
                    font-size: 1.4em;
                    color: #555;
                }
                </style>
                """

                def substep(icon, title, desc):
                    return f"""
                    <div class="substep-item">
                        <div class="substep-icon">{icon}</div>
                        <div>
                            <div class="substep-text"><b>{title}</b></div>
                            <div style="font-size:0.75em;color:#888">{desc}</div>
                        </div>
                    </div>
                    """

                nodes_html = '<div class="flow-container">'

                for i, step in enumerate(trace):
                    agent = step.get("agent", "Unknown Agent")
                    model = step.get("model", "Unknown")

                    substeps_html = ""

                    if "Founder" in agent:
                        substeps_html += substep("🧠", "Refine Idea", "Synthesising initial concept")
                    elif "Market" in agent:
                        substeps_html += substep("🔍", "Search Market", "Validating demand")
                        substeps_html += substep("🧠", "Analyze", "Extracting insights")
                    elif "Competitor" in agent:
                        substeps_html += substep("🏢", "Competitor Scan", "Mapping alternatives")
                    elif "Pricing" in agent:
                        substeps_html += substep("💸", "Pricing Model", "Evaluating monetization")
                    elif "MVP" in agent:
                        substeps_html += substep("🛠️", "MVP Scope", "Defining build plan")
                    elif "Skeptic" in agent:
                        substeps_html += substep("⚖️", "Risk Review", "Challenging assumptions")
                    else:
                        # 🚨 GUARANTEED FALLBACK (prevents broken HTML)
                        substeps_html += substep("🤖", "Process", "Agent execution")

                    nodes_html += f"""
                    <div class="agent-node">
                        <div class="agent-header">
                            <span class="agent-title">{agent}</span>
                            <span class="model-badge">🤖 {model}</span>
                        </div>
                        <div class="substep-container">
                            {substeps_html}
                        </div>
                    </div>
                    """

                    if i < len(trace) - 1:
                        nodes_html += '<div class="connector">↓</div>'

                nodes_html += "</div>"

                components.html(
                    flow_css + nodes_html,
                    height=900,
                    scrolling=True
                )


            st.subheader("Detailed Execution Trace")
            if not trace:
                st.warning("No trace data available.")
            
            for step in trace:
                with st.expander(f"🧩 {step.get('agent')} ({step.get('step')})"):
                    st.markdown("### 📝 Prompt")
                    st.code("\n\n".join(step.get('prompt', [])), language="text")
                    
                    tools = step.get('tool_calls', [])
                    if tools:
                        st.markdown("### 🛠️ Tool Calls")
                        for t in tools:
                            tool_name = t.get('tool')
                            if tool_name == 'serper':
                                st.write(f"**🔍 Google Search (Serper):** `{t.get('query')}`")
                                st.markdown("##### Explore Search Results")
                                results = t.get('output')
                                if isinstance(results, list) and results:
                                    for idx, res in enumerate(results):
                                        st.markdown(f"**{idx+1}.** {res}")
                                        st.divider()
                                elif not results:
                                    st.warning("No results found.")
                                else:
                                    st.json(results)
                            elif tool_name == 'faiss_retrieval':
                                st.write(f"**📚 Knowledge Retrieval (RAG):** `{t.get('query')}`")
                                st.markdown("##### View Retrieved Context")
                                results = t.get('output')
                                if isinstance(results, list) and results:
                                    for idx, res in enumerate(results):
                                        st.info(f"**Chunk {idx+1}:**\n\n{res}")
                                else:
                                    st.warning("No relevant context found.")
                            else:
                                st.write(f"**Tool:** `{tool_name}`")
                                st.write(f"**Input:** `{t.get('query')}`")
                                st.json(t.get('output'))
                            st.divider()
                    
                    st.markdown("### 🤖 LLM Response")
                    st.write(step.get('llm_response'))
main()