# Phase 4 To-Do: Tool Calling & Security Architecture

## Database Security
- [x] Create restricted `agent_user`
- [x] Configure RBAC permissions
- [x] Restrict dangerous SQL operations

## Tool Layer
- [x] Implement `execute_business_query`
- [x] Add forbidden keyword filtering
- [x] Create MCP-compatible wrappers (db_tools.py)
- [x] Add schema viewer tool

## Security Layer
- [x] Create security system prompt
- [x] Block infrastructure disclosure (via Prompt & Tools)
- [x] Add jailbreak protection (core/utils/security.py)

## Testing
- [x] Test blocked DROP TABLE
- [x] Test safe SELECT queries
- [x] Test RBAC restrictions

## UI Validation
- [x] Streamlit displays security warning
- [x] Dangerous commands are rejected (via is_jailbreak_attempt and SQL filter)
- [x] Trace logs show blocked execution
