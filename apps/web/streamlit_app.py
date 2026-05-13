from __future__ import annotations
import os
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
API_HOST = os.getenv("API_HOST", "http://localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"{API_HOST}:{API_PORT}"


def call_agent(prompt: str, thread_id: str | None = None) -> dict[str, object]:
    response = requests.post(
        f"{API_URL}/v1/agent/chat",
        json={"prompt": prompt, "thread_id": thread_id},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def load_history() -> list[dict[str, str]]:
    return st.session_state.get("history", [])


def append_history(entry: dict[str, str]) -> None:
    history = load_history()
    history.append(entry)
    st.session_state.history = history


def run_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun() # type: ignore


def main() -> None:
    st.set_page_config(page_title="Agentic CRM UI", page_icon="🤖", layout="wide")
    st.title("Agentic CRM Phase 2 UI")
    st.markdown(
        "Use this dashboard to send prompts to the API, view trace output, and inspect audit logs."
    )

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "trace_response" not in st.session_state:
        st.session_state.trace_response = None

    sidebar = st.sidebar
    sidebar.header("Agent Session")
    sidebar.text_input("Current thread", value=st.session_state.thread_id, disabled=True)

    if sidebar.button("Reset session"):
        st.session_state.thread_id = ""
        st.session_state.history = []
        st.session_state.trace_response = None
        run_rerun()

    sidebar.markdown("---")
    sidebar.subheader("Service status")
    try:
        status = requests.get(f"{API_URL}/health", timeout=5).json()
        sidebar.success("API available")
        sidebar.json(status)
    except requests.RequestException as exc:
        sidebar.error(f"API unavailable: {exc}")

    sidebar.markdown("---")
    sidebar.markdown("#### API Settings")
    sidebar.text_input("API URL", value=API_URL, disabled=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Send prompt")
        with st.form("prompt_form", clear_on_submit=False):
            prompt = st.text_area("Prompt", height=180, placeholder="Ask the Agent about CRM data, workflows, or debug traces...")
            submitted = st.form_submit_button("Send")
            if submitted and prompt.strip():
                try:
                    result = call_agent(prompt, st.session_state.thread_id or None)
                    st.session_state.thread_id = result.get("thread_id", st.session_state.thread_id)
                    append_history(
                        {
                            "prompt": prompt,
                            "response": result.get("result", ""),
                            "thread_id": st.session_state.thread_id,
                        } # type: ignore
                    )
                    st.success("Prompt sent successfully")
                    run_rerun()
                except requests.RequestException as exc:
                    st.error(f"API request failed: {exc}")

        st.subheader("Conversation history")
        for item in reversed(load_history()):
            with st.expander(f"Prompt: {item['prompt']}", expanded=False):
                st.markdown(f"**Response:**\n{item['response']}")
                st.caption(f"thread_id: {item['thread_id']}")

    with col2:
        st.subheader("Trace viewer")
        thread_input = st.text_input("Trace thread ID", value=st.session_state.thread_id)
        if st.button("Load trace") and thread_input.strip(): # type: ignore
            try:
                trace = requests.get(f"{API_URL}/v1/agent/trace/{thread_input.strip()}", timeout=20).json() # pyright: ignore[reportOptionalMemberAccess]
                st.session_state.trace_response = trace
            except requests.RequestException as exc:
                st.error(f"Failed to load trace: {exc}")

        if st.session_state.trace_response:
            st.json(st.session_state.trace_response)
        else:
            st.info("Trace result will appear here after loading a thread ID.")

        st.markdown("---")
        st.subheader("SQL debug placeholder")
        st.code("-- SQL debug is not enabled in Phase 2; trace metadata is available in the UI.")


if __name__ == "__main__":
    main()
