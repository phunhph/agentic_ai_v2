import pytest
from core.graph.langgraph_runtime import LangGraphRuntime
from core.agents.ingest_agent import IngestAgent

def test_full_pipeline_e2e():
    """Test the full end-to-end flow from Ingestion to Execution and Reflection."""
    runtime = LangGraphRuntime()
    ingest = IngestAgent()
    
    prompt = "Please count the total number of accounts in the system"
    thread_id = "test_thread_e2e"
    session_id = "test_tenant"
    
    # 1. Ingestion Phase
    ingest_state = ingest.process(prompt, thread_id, session_id)
    
    assert "intent" in ingest_state
    assert "detected_language" in ingest_state
    
    # 2. Execution Phase (LangGraph Runtime)
    # The runtime covers reasoning, planning, execution, reflection and learning
    response = runtime.run(
        thread_id=thread_id,
        prompt=prompt,
        session_id=session_id,
        ingest_state=ingest_state
    )
    
    assert "result" in response
    assert "trace" in response
    
    assert response["reasoning_state"]["business_intent"] is not None
    assert response["planning_state"]["task_count"] > 0
    
    # Check if execution tasks are present
    assert len(response["execution_state"]["tasks"]) > 0
    
    # Verify final text generation
    assert len(response["result"]) > 0
