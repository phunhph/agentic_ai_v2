# Phase 20 To-Do: Autonomous Tool Discovery & MCP Integration

## 1. MCP Integration Layer
- [x] Implement `MCP Client` to interface with Model Context Protocol servers
- [x] Create `mcp_config.json` for external service configurations
- [x] Implement `npx` based server launching for MCP plugins (Postgres, Filesystem, etc.)

## 2. Autonomous Tool Discovery
- [x] Implement `Discovery Node` to list available tools from MCP servers at runtime
- [x] Remove hard-coded tool schemas from Agent prompts
- [x] Implement `Dynamic Tool Matching` (AI decides which MCP tool to use on the fly)

## 3. Specialized MCP Servers
- [x] Deploy `Postgres MCP` for standard SQL operations
- [x] Deploy `Filesystem MCP` for report generation and file handling
- [x] (Optional) Integrate standard MCPs for Slack, GitHub, or Google Drive

## 4. Security & Isolation
- [x] Implement `Security Sandboxing` for external tool execution
- [x] Implement permission controls at the MCP server level
- [x] Audit tool usage for data leakage or unauthorized access

## 5. Scalability & Maintenance
- [x] Transition codebase to "Lean Core" architecture (minimal built-in tools)
- [x] Implement `Auto-discovery` on system startup
- [x] Verify "Plug-and-play" capability (adding new tools without code changes)
