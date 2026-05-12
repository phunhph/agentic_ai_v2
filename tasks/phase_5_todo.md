# Phase 5 To-Do: IngestAgent Layer (The Gatekeeper)

## Core Implementation
- [x] Implement `ingest_agent_node`
- [x] Connect Gemini Flash (via litellm)
- [x] Parse structured JSON output
- [x] Append trace logs

## Security
- [x] Detect prompt injection (via Security Prompt)
- [x] Detect system probing
- [x] Block dangerous requests
- [x] Stop workflow on violations (LangGraph Conditional Edges)

## Entity Extraction
- [x] Detect account names
- [x] Detect dates
- [x] Detect CRM entities
- [x] Use db metadata awareness

## Ambiguity Handling
- [x] Detect vague prompts
- [x] Generate refined questions
- [x] Prevent hallucinated assumptions

## UI Integration
- [x] Display ingest trace in sidebar
- [x] Show extracted entities
- [x] Show security status
