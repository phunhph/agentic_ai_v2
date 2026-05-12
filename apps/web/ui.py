import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests
import uuid
import time
import json

# --- Page Config ---
st.set_page_config(
    page_title="Agentic CRM Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    /* Dark Mode Theme */
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #1e293b;
        border: 1px solid #334155;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #0f172a;
        border: 1px solid #1e3a8a;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e3a8a;
    }
    
    /* Custom Info Box for Trace */
    .trace-card {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
    }
    
    /* Glassmorphism effect */
    .glass {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Agent Monitoring ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("CRM Intelligence")
    st.markdown("---")
    
    st.subheader("🕵️ Real-time Agent Trace")
    trace_container = st.container()
    
    st.markdown("---")
    st.subheader("📊 Performance Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latency", "1.2s", "-5%")
    with col2:
        st.metric("Tokens", "154", "+2%")

# --- Main Interface ---
st.title("🚀 Autonomous CRM System")
st.caption("Powered by LangGraph, Groq & Gemini")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_trace" not in st.session_state:
    st.session_state.latest_trace = []
if "latest_details" not in st.session_state:
    st.session_state.latest_details = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Hỏi tôi về doanh thu, khách hàng hoặc hợp đồng..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call Backend API
    with st.spinner("Agentic đang suy nghĩ..."):
        try:
            # Fake thread_id for now
            thread_id = str(uuid.uuid4())
            
            # Request to Flask
            response = requests.post(
                "http://localhost:5000/v1/agent/chat",
                json={"query": prompt, "thread_id": thread_id},
                timeout=30
            )
            
            if response.status_code == 200:
                # Log raw response for debugging
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    st.error(f"Backend không trả về JSON. Content-Type: {content_type}")
                    st.code(response.text)
                    st.stop()
                
                try:
                    result = response.json()
                except Exception as json_err:
                    st.error(f"Lỗi Parse JSON: {json_err}")
                    st.code(response.text)
                    st.stop()
                
                answer = result.get("answer", "Xin lỗi, tôi gặp sự cố khi xử lý.")
                
                # Update session state with new trace data
                st.session_state.latest_trace = result.get("trace_log", [])
                st.session_state.latest_details = result.get("trace_details", [])
                
                # Display assistant message
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    
                    if "sql_query" in result and result["sql_query"]:
                        with st.expander("🛠️ Generated SQL Query"):
                            st.code(result["sql_query"], language="sql")
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Lỗi hệ thống: {response.status_code}")
        except Exception as e:
            st.error(f"Không thể kết nối tới Backend: {e}")

# Render trace in sidebar
with trace_container:
    if st.session_state.latest_trace:
        # Map logs to details by index
        for i, log in enumerate(st.session_state.latest_trace):
            detail = st.session_state.latest_details[i] if i < len(st.session_state.latest_details) else {}
            
            with st.expander(f"🔍 {log}"):
                if detail:
                    st.markdown("**📥 Input:**")
                    st.json(detail.get("input", "N/A"))
                    st.markdown("**📤 Output:**")
                    st.json(detail.get("output", "N/A"))
                else:
                    st.write("Không có dữ liệu chi tiết.")
    else:
        st.write("Chưa có tiến trình nào.")

# Auto-scroll or Rerun if needed
if prompt:
    st.rerun()
