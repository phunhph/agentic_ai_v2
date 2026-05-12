import os
from dotenv import load_dotenv

load_dotenv()

def setup_tracing():
    """
    Configures LangSmith and Phoenix tracing if API keys are present.
    """
    # LangSmith
    if os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "agentic-crm")
        print("🚀 LangSmith Tracing Enabled")

    # Phoenix (Arize)
    if os.getenv("PHOENIX_PORT"):
        import phoenix as px
        px.launch_app(port=int(os.getenv("PHOENIX_PORT", 6006)))
        print(f"🔥 Phoenix Tracing Enabled on port {os.getenv('PHOENIX_PORT')}")

def get_monitoring_summary(state):
    """
    Utility to format execution metrics for the UI.
    """
    return {
        "retry_count": state.get("retry_count", 0),
        "steps_completed": len(state.get("steps_completed", [])),
        "latency_logs": state.get("trace_log", [])
    }
