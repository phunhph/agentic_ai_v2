# Phase 21 To-Do: The Observability Cockpit & Trace Visualization

## 1. Backend Telemetry System
- [x] Implement `Node Tracker` to capture inputs, outputs, and reasoning per LangGraph node
- [x] Implement `Execution Trace` data model (linked to request ID)
- [x] Create `core/monitor/tracker.py` for automated behavior logging

## 2. Observability Cockpit UI
- [x] Create `ui_cockpit.py` in Streamlit for real-time trace visualization
- [x] Implement `Live Execution Trace` viewer (Tree or Timeline view)
- [x] Add `Expandable Steps` to inspect node-level inputs, outputs, and confidence

## 3. "Why Engine" & Insights
- [x] Implement `Reasoning Explanation` capture (capturing AI's internal thoughts)
- [x] Implement `Learning Insights` display (showing which RAG patterns were matched)
- [x] Add `Cost Attribution` per node (displaying USD/Tokens spent per step)

## 4. Debugging & Optimization Tools
- [x] Implement `Proactive Bottleneck Detection` (alerts for slow nodes)
- [x] Create `Latency Map` and `Execution Heatmap` visualizations
- [x] Implement `Replay Engine` to re-run historical requests with different settings

## 5. Verification & Verification
- [x] Verify "Full Transparency" (every AI decision is traceable)
- [x] Benchmark UI responsiveness with trace capture enabled
- [x] Audit the system's "Observability-first" architecture impact
