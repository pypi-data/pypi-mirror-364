"""
Tests for the MCP server implementation.

This module tests the core MCP server functionality including
tool registration, protocol compliance, and request handling.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.server import TodoMCPServer


@pytest.fixture
def config():
    """Create a test configuration."""
    return TodoConfig(
        data_directory="test_data",
        log_level="DEBUG",
        performance_monitoring=False
    )


@pytest.fixture
def server(config):
    """Create a test server instance."""
    return TodoMCPServer(config)


class TestTodoMCPServer:
    """Test cases for TodoMCPServer."""
    
    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.config is not None
        assert server.task_service is not None
        assert server.server is not None
        assert server.logger is not None
    
    def test_tool_definitions(self, server):
        """Test tool definitions are properly structured."""
        tools = server._get_tool_definitions()
        
        # Check we have the expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "create_task", "update_task", "delete_task", "get_task", "list_tasks",
            "update_task_status", "get_pending_tasks", "get_in_progress_tasks",
            "get_blocked_tasks", "get_completed_tasks",
            "add_child_task", "get_task_hierarchy",
            "search_tasks", "get_task_statistics"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"
        
        # Check tool structure
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            assert isinstance(tool.inputSchema, dict)
            assert tool.inputSchema.get('type') == 'object'
    
    def test_create_task_tool_schema(self, server):
        """Test create_task tool has proper schema."""
        tools = server._get_tool_definitions()
        create_task_tool = next(tool for tool in tools if tool.name == "create_task")
        
        schema = create_task_tool.inputSchema
        assert 'properties' in schema
        assert 'title' in schema['properties']
        assert 'required' in schema
        assert 'title' in schema['required']
        
        # Check title property
        title_prop = schema['properties']['title']
        assert title_prop['type'] == 'string'
        assert 'description' in title_prop
    
    @pytest.mark.asyncio
    async def test_tool_call_routing(self, server):
        """Test tool calls are routed correctly."""
        # Mock the task service
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        # Mock the tool function
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_create:
            mock_create.return_value = {"success": True, "task_id": "test_123"}
            
            result = await server._handle_tool_call("create_task", {"title": "Test Task"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "success" in result[0].text
            mock_create.assert_called_once_with({"title": "Test Task"})
    
    @pytest.mark.asyncio
    async def test_tool_call_error_handling(self, server):
        """Test error handling in tool calls."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        # Mock the tool function to raise an error
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_create:
            mock_create.side_effect = ValueError("Test error")
            
            result = await server._handle_tool_call("create_task", {"title": "Test Task"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Error executing create_task" in result[0].text
            assert "Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_unknown_tool_error(self, server):
        """Test handling of unknown tool calls."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        result = await server._handle_tool_call("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Unknown tool: unknown_tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_task_service_initialization(self, server):
        """Test task service is initialized when needed."""
        # Mock task service
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = False
        
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_create:
            mock_create.return_value = {"success": True}
            
            await server._handle_tool_call("create_task", {"title": "Test"})
            
            server.task_service.initialize.assert_called_once()
    
    def test_all_tool_handlers_exist(self, server):
        """Test that all tool handlers are implemented."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            handler_name = f"_handle_{tool.name}"
            assert hasattr(server, handler_name), f"Missing handler: {handler_name}"
            
            handler = getattr(server, handler_name)
            assert callable(handler), f"Handler {handler_name} is not callable"


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance."""
    
    def test_tool_schema_compliance(self, server):
        """Test tool schemas comply with JSON Schema standards."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            schema = tool.inputSchema
            
            # Basic JSON Schema requirements
            assert isinstance(schema, dict)
            assert schema.get('type') == 'object'
            
            if 'properties' in schema:
                assert isinstance(schema['properties'], dict)
                
                for prop_name, prop_schema in schema['properties'].items():
                    assert isinstance(prop_schema, dict)
                    assert 'type' in prop_schema or 'enum' in prop_schema
            
            if 'required' in schema:
                assert isinstance(schema['required'], list)
                for required_prop in schema['required']:
                    assert required_prop in schema.get('properties', {})
    
    def test_tool_names_valid(self, server):
        """Test tool names follow MCP conventions."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            # Tool names should be valid identifiers
            assert tool.name.replace('_', '').isalnum()
            assert not tool.name.startswith('_')
            assert not tool.name.endswith('_')
    
    def test_tool_descriptions_present(self, server):
        """Test all tools have descriptions."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            assert tool.description
            assert len(tool.description.strip()) > 0
            assert isinstance(tool.description, str)


@pytest.mark.integration
class TestServerIntegration:
    """Integration tests for the MCP server."""
    
    @pytest.mark.asyncio
    async def test_server_lifecycle(self, config):
        """Test server startup and shutdown."""
        server = TodoMCPServer(config)
        
        # Mock stdio_server to avoid actual I/O
        with patch('src.todo_mcp.server.stdio_server') as mock_stdio:
            mock_stdio.return_value.__aenter__.return_value = (
                AsyncMock(), AsyncMock()
            )
            
            # Mock the server run method to avoid infinite loop
            server.server.run = AsyncMock()
            
            # Test server run
            await server.run()
            
            # Verify initialization was called
            server.server.run.assert_called_once()