from core.graph.langgraph_runtime import LangGraphRuntime
from core.utils.llm import LLMClient


def test_build_result_falls_back_on_llm_rate_limit(monkeypatch):
    runtime = LangGraphRuntime()

    def raise_rate_limit(self, *args, **kwargs):
        raise RuntimeError("Rate limit exceeded for model")

    monkeypatch.setattr(LLMClient, "completion", raise_rate_limit)

    result = runtime._build_result(
        prompt="List the customer accounts.",
        model="grok/llama-3.3-70b-versatile",
        schema_context={"views": [], "details": []},
        reasoning_state={"detected_language": "en", "business_intent": "List accounts"},
        planning_state={"task_count": 1},
        execution_state={"status": "success", "tasks": [{"description": "Query accounts", "result": {"rows": [{"id": 1}, {"id": 2}]}}]},
        reflection_state={"status": "success", "issues": []},
        sql_preview=None,
        retry_attempts=[],
        dlq_record=None,
    )

    assert "Yêu cầu đã được thực thi thành công" in result
    assert "2 bản ghi" in result
