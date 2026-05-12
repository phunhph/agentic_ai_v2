import subprocess
import json

class MCPClient:
    """
    Phase 20: Autonomous Tool Discovery & MCP Integration.
    Hỗ trợ kết nối các server MCP bên ngoài.
    """
    
    def discover_tools(self, server_name: str) -> list:
        """Khám phá các tool từ một MCP server thông qua CLI."""
        try:
            # Ví dụ gọi npx để list tools từ một MCP server
            result = subprocess.run(
                ["npx", "-y", server_name, "list-tools"], 
                capture_output=True, text=True, timeout=10
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"MCP Discovery Error: {e}")
            return []

    def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        """Thực thi một tool thông qua MCP."""
        try:
            result = subprocess.run(
                ["npx", "-y", server_name, "call-tool", tool_name, json.dumps(arguments)],
                capture_output=True, text=True, timeout=30
            )
            return json.loads(result.stdout)
        except Exception as e:
            return {"status": "error", "message": str(e)}
