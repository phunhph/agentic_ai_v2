import streamlit as st
import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.utils.infra.db import query
from core.utils.logic.cost_router import CostRouter

st.set_page_config(page_title="Observability Cockpit", page_icon="🔭", layout="wide")

st.title("🔭 Observability Cockpit")
st.markdown("Phase 7: Real-time Cost, Bottlenecks, and Analytics.")

# 1. Cost & Budget Metrics
st.header("1. Cost Guardrails & Budget")
col1, col2, col3 = st.columns(3)

router = CostRouter()
total_spent = router.__class__._total_cost_spent
daily_budget = router.daily_budget
circuit_failures = router.__class__._consecutive_failures

with col1:
    st.metric("Total Cost Spent (USD)", f"${total_spent:.4f}", help="Estimated LLM cost in current session")
with col2:
    st.metric("Daily Budget (USD)", f"${daily_budget:.4f}")
with col3:
    status = "TRIPPED" if router.__class__._circuit_open_until > 0 else "OK"
    st.metric("Circuit Breaker Status", status, delta=f"{circuit_failures} failures", delta_color="inverse")

st.progress(min(total_spent / daily_budget, 1.0))

st.markdown("---")

# 2. Performance & Error Analytics
st.header("2. Execution Analytics")

try:
    # Query system metrics
    metrics = query("SELECT metric_name, metric_value, tags, created_at FROM audit_zone.system_metrics ORDER BY created_at DESC LIMIT 100")
    if metrics:
        df_metrics = pd.DataFrame(metrics)
        st.subheader("Recent Metrics")
        st.dataframe(df_metrics, use_container_width=True)
    else:
        st.info("No system metrics found.")
        
    # Query logs to get success/fail rate
    logs = query("SELECT event_type, payload, created_at FROM audit_zone.agent_logs WHERE event_type IN ('execution', 'reflection') ORDER BY created_at DESC LIMIT 500")
    if logs:
        fail_count = 0
        pass_count = 0
        for row in logs:
            payload = row.get("payload", {})
            if isinstance(payload, str):
                import json
                try:
                    payload = json.loads(payload)
                except:
                    continue
                    
            status = payload.get("status")
            if status in ["fail", "failed", "rejected"]:
                fail_count += 1
            elif status in ["pass", "success", "completed"]:
                pass_count += 1
                
        total = pass_count + fail_count
        if total > 0:
            st.subheader(f"Recent Success Rate: {(pass_count/total)*100:.1f}%")
            colA, colB = st.columns(2)
            colA.metric("Successful Executions", pass_count)
            colB.metric("Failed Executions", fail_count)
            
    else:
        st.info("No execution logs found.")
        
except Exception as e:
    st.error(f"Could not load analytics from database: {e}")

st.markdown("---")
st.header("3. Recent Agent Traces")

try:
    traces = query("SELECT thread_id, event_type, created_at FROM audit_zone.agent_logs WHERE event_type = 'request' ORDER BY created_at DESC LIMIT 10")
    if traces:
        st.dataframe(pd.DataFrame(traces), use_container_width=True)
    else:
        st.info("No traces found.")
except Exception as e:
    st.error(f"Could not load traces: {e}")
