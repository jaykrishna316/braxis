"""Tests for Braxis MCP Server integration."""

import json
import unittest
from pathlib import Path

from src.braxis.mcp_server import BraxisServer
from src.braxis.mcp_stdio import MCPHandler


class TestBraxisServer(unittest.TestCase):
    """Test BraxisServer core functionality."""

    def setUp(self):
        """Initialize server for testing."""
        self.server = BraxisServer()

    def test_get_tools(self):
        """Test that tools are properly defined."""
        tools = self.server.get_tools()

        self.assertEqual(len(tools), 4)
        tool_names = {tool["name"] for tool in tools}

        self.assertIn("analyze_repository", tool_names)
        self.assertIn("extract_patterns", tool_names)
        self.assertIn("generate_agents_md", tool_names)
        self.assertIn("get_readiness_score", tool_names)

    def test_analyze_repository_invalid_path(self):
        """Test error handling for invalid repository path."""
        result = self.server.analyze_repository("/nonexistent/path")

        self.assertIn("error", result)

    def test_extract_patterns_invalid_type(self):
        """Test error handling for invalid pattern type."""
        result = self.server.extract_patterns("/some/path", "invalid_type")

        self.assertIn("error", result)

    def test_process_tool_call_unknown_tool(self):
        """Test error handling for unknown tool."""
        result = self.server.process_tool_call(
            "unknown_tool", {"repo_path": "/some/path"}
        )

        self.assertIn("error", result)

    def test_tool_definitions_have_input_schema(self):
        """Test that all tools have proper input schemas."""
        tools = self.server.get_tools()

        for tool in tools:
            self.assertIn("inputSchema", tool)
            self.assertIn("type", tool["inputSchema"])
            self.assertIn("properties", tool["inputSchema"])
            self.assertIn("required", tool["inputSchema"])


class TestMCPHandler(unittest.TestCase):
    """Test MCP Protocol Handler."""

    def setUp(self):
        """Initialize handler for testing."""
        self.handler = MCPHandler()

    def test_initialize_request(self):
        """Test initialize request handling."""
        message = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

        response = self.handler.process_message(message)

        self.assertEqual(response["id"], 1)
        self.assertIn("result", response)
        self.assertIn("protocolVersion", response["result"])
        self.assertIn("serverInfo", response["result"])

    def test_list_tools_request(self):
        """Test tools/list request handling."""
        message = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        response = self.handler.process_message(message)

        self.assertEqual(response["id"], 2)
        self.assertIn("result", response)
        self.assertIn("tools", response["result"])
        self.assertGreater(len(response["result"]["tools"]), 0)

    def test_unknown_method(self):
        """Test handling of unknown method."""
        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "unknown/method",
            "params": {},
        }

        response = self.handler.process_message(message)

        self.assertEqual(response["id"], 3)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)

    def test_call_tool_with_error(self):
        """Test tool call with error handling."""
        message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "analyze_repository", "arguments": {"repo_path": "/x"}},
        }

        response = self.handler.process_message(message)

        self.assertEqual(response["id"], 4)
        self.assertIn("result", response)

    def test_server_info(self):
        """Test that server info is properly set."""
        message = {"jsonrpc": "2.0", "id": 5, "method": "initialize", "params": {}}

        response = self.handler.process_message(message)

        server_info = response["result"]["serverInfo"]
        self.assertEqual(server_info["name"], "braxis")
        self.assertEqual(server_info["version"], "3.0.0")


class TestMCPIntegration(unittest.TestCase):
    """Integration tests for MCP server."""

    def setUp(self):
        """Initialize server and handler."""
        self.handler = MCPHandler()

    def test_initialization_workflow(self):
        """Test typical initialization workflow."""
        # Initialize
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
        init_response = self.handler.process_message(init_message)
        self.assertIn("result", init_response)

        # List tools
        list_message = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        list_response = self.handler.process_message(list_message)
        self.assertIn("result", list_response)
        self.assertGreater(len(list_response["result"]["tools"]), 0)

    def test_json_serialization(self):
        """Test that all responses are JSON serializable."""
        message = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

        response = self.handler.process_message(message)

        # Should not raise an exception
        json_str = json.dumps(response)
        self.assertIsInstance(json_str, str)

    def test_tool_response_format(self):
        """Test that tool responses have correct format."""
        message = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

        response = self.handler.process_message(message)

        self.assertIn("jsonrpc", response)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("id", response)
        self.assertIn("result", response)
        self.assertNotIn("error", response)


if __name__ == "__main__":
    unittest.main()
