"""MCP Protocol Handler - Implements Model Context Protocol over stdio."""

import json
import sys
from typing import Any, Dict, Optional

from src.braxis.mcp_server import BraxisServer


class MCPHandler:
    """Handles MCP protocol messages over stdio."""

    def __init__(self):
        """Initialize MCP handler and Braxis server."""
        self.server = BraxisServer()
        self.version = "3.0.0"
        self.name = "braxis"

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False,
                },
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version,
            },
        }

    def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {"tools": self.server.get_tools()}

    def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        tool_input = params.get("arguments", {})

        result = self.server.process_tool_call(tool_name, tool_input)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2),
                }
            ]
        }

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP message and return response."""
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
        }

        try:
            if method == "initialize":
                response["result"] = self.handle_initialize(params)
            elif method == "tools/list":
                response["result"] = self.handle_list_tools(params)
            elif method == "tools/call":
                response["result"] = self.handle_call_tool(params)
            elif method == "completion/complete":
                response["result"] = {"completion": ""}
            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                }
        except Exception as e:
            response["error"] = {
                "code": -32603,
                "message": f"Internal error: {str(e)}",
            }

        return response


def run_server():
    """Run the MCP server over stdio."""
    handler = MCPHandler()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
            response = handler.process_message(message)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}",
                },
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    run_server()
