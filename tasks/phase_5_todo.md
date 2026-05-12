# Phase 5 To-Do: IngestAgent Layer (The Gatekeeper)

## Core Implementation
- [ ] Implement `ingest_agent_node`
- [ ] Connect Gemini Flash
- [ ] Parse structured JSON output
- [ ] Append trace logs

## Security
- [ ] Detect prompt injection
- [ ] Detect system probing
- [ ] Block dangerous requests
- [ ] Stop workflow on violations

## Entity Extraction
- [ ] Detect account names
- [ ] Detect dates
- [ ] Detect CRM entities
- [ ] Use db metadata awareness

## Ambiguity Handling
- [ ] Detect vague prompts
- [ ] Generate refined questions
- [ ] Prevent hallucinated assumptions

## UI Integration
- [ ] Display ingest trace in sidebar
- [ ] Show extracted entities
- [ ] Show security status
