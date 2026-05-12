# Phase 4 To-Do: Tool Calling & Security Architecture

## Database Security
- [ ] Create restricted `agent_user`
- [ ] Configure RBAC permissions
- [ ] Restrict dangerous SQL operations

## Tool Layer
- [ ] Implement `execute_business_query`
- [ ] Add forbidden keyword filtering
- [ ] Create MCP-compatible wrappers
- [ ] Add schema viewer tool

## Security Layer
- [ ] Create security system prompt
- [ ] Block infrastructure disclosure
- [ ] Add jailbreak protection

## Testing
- [ ] Test blocked DROP TABLE
- [ ] Test safe SELECT queries
- [ ] Test RBAC restrictions

## UI Validation
- [ ] Streamlit displays security warning
- [ ] Dangerous commands are rejected
- [ ] Trace logs show blocked execution
